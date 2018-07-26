#  Copyright (c) 2015 SONATA-NFV, 5GTANGO, UBIWHERE, Paderborn University
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO, UBIWHERE, Paderborn University,
# Quobis nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has also been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.5gtango.eu).
import logging
import os
import json
import time
import hashlib
import tempfile
import requests
import shutil
# import ast
import subprocess
import urllib.request as urllib2
import urllib.parse as urlparse
from flask import Flask, Blueprint, request
from flask_restplus import Resource, Api, Namespace
from flask_restplus import fields, inputs
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from requests.exceptions import RequestException
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from flask_cors import CORS
from flask_caching import Cache, make_template_fragment_key

from tngsdk.validation import cli
from tngsdk.validation.validator import Validator
from tngsdk.validation.event import EventLogger
from tngsdk.project.workspace import Workspace

# To implement watchdogs to subscribe to changes in any descriptor file
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

log = logging.getLogger(os.path.basename(__file__))


app = Flask(__name__)
app.config.from_pyfile('rest_settings.py')

if app.config['ENABLE_CORS']:
        CORS(app)

app.wsgi_app = ProxyFix(app.wsgi_app)
blueprint = Blueprint('api', __name__, url_prefix="/api")
api_v1 = Namespace("v1", description="tng-validation API v1")
api = Api(blueprint,
          version="0.1",
          title='5GTANGO tng-sdk-validation API',
          description="5GTANGO tng-validation REST API " +
          "to validate descriptors.")
app.register_blueprint(blueprint)
api.add_namespace(api_v1)

# This file should be generated with Swagger form an
#  OpenAPI file, shouldn't it?

# Define Redis username and pass

# config cache
if app.config['CACHE_TYPE'] == 'redis':

    redis_auth = app.config['REDIS_USER'] + ':' + app.config[
        'REDIS_PASSWD'] + '@' \
        if app.config['REDIS_USER'] and app.config['REDIS_PASSWD'] else ''
    redis_url = 'redis://' + redis_auth + app.config['REDIS_HOST'] + \
                ':' + app.config['REDIS_PORT']

    cache = Cache(app, config={'CACHE_TYPE': 'redis',
                               'CACHE_DEFAULT_TIMEOUT': 0,
                               'CACHE_REDIS_URL': redis_url})

elif app.config['CACHE_TYPE'] == 'simple':
    cache = Cache(app, config={'CACHE_TYPE': 'simple',
                               'CACHE_DEFAULT_TIMEOUT': 0})

else:
    print("Invalid cache type.")
    sys.exit(1)

# keep temporary request errors
req_errors = []


class Validatewatchers(FileSystemEventHandler):
    def __init__(self, path, callback, filename=None):
        self.path = path
        self.filename = filename
        self.callback = callback
        self.observer = Observer()
        self.observer.schedule(self, self.path,
                               recursive=False if self.filename else True)
        self.observer.start()
        # self.observer.join()

    def on_modified(self, event):
        print(self.filename)
        print(event.src_path)
        print(event)

        self.observer.stop()
        self.callback(self.path + '/' + self.filename)


def initialize(debug=False):
    log.info("Initializing validator service")

    cache.clear()
    cache.add('debug', debug)
    cache.add('artifacts', list())
    cache.add('validations', dict())
    cache.add('resources', dict())
    cache.add('latest', dict())
    cache.add('watchers', dict())

    os.makedirs(app.config['ARTIFACTS_DIR'], exist_ok=True)
    set_artifact(app.config['ARTIFACTS_DIR'])

# def dump_swagger(args):
#     # TODO replace this with the URL of a real tng-package service
#     app.config.update(SERVER_NAME="tng-package.5gtango.eu")
#     with app.app_context():
#         with open(args.dump_swagger_path, "w") as f:
#             # TODO dump in nice formatting
#             f.write(json.dumps(api.__schema__))


def serve_forever(args, debug=True):
    """
    Start REST API server. Blocks.
    """
    # TODO replace this with WSGIServer for better performance
    app.cliargs = args
    if (args.mode == 'local' and args.workspace_path):
        ws_root = os.path.expanduser(args.workspace_path)
        log.info(ws_root)
        ws = Workspace.__create_from_descriptor__(ws_root)
        if not ws:
            log.error("Could not find a SONATA workspace at "
                      "at the specified location")
            exit(1)
        load_watch_dirs(ws)

    app.run(host=args.service_address,
            port=args.service_port,
            debug=debug)


ping_get_return_model = api_v1.model("PingGetReturn", {
    "ping": fields.String(
        description="pong",
        required=True),
    "uptime": fields.String(
        description="system uptime",
        required=True),
})


validations_parser = api_v1.parser()
validations_parser.add_argument("syntax",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="syntax check")
validations_parser.add_argument("integrity",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="integrity check")
validations_parser.add_argument("topology",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="topology check")
validations_parser.add_argument("custom",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="custom rules check")
validations_parser.add_argument("function",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="Function validation")
validations_parser.add_argument("service",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="Service validation")
validations_parser.add_argument("project",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="If True indicates that the request "
                                     "if for a project validation")
validations_parser.add_argument("workspace",
                                location="args",
                                required=False,
                                help="Specify the directory of the SDK " +
                                     "workspace for validating the " +
                                     " SDK project.")
validations_parser.add_argument("sync",
                                location="args",
                                type=inputs.boolean,
                                required=False,
                                help="If True indicates that the request"
                                     " will be handled synchronously")
validations_parser.add_argument("dpath",
                                location="args",
                                required=False,
                                help="Specify a directory to search for "
                                     "descriptors. Particularly useful"
                                     " when using the '--service' argument.")
validations_parser.add_argument("path",
                                location="args",
                                required=False,
                                help="Specify a directory to search for "
                                     "descriptors. Used when the 'source' is"
                                     " 'local' or 'url'.")
validations_parser.add_argument("dext",
                                location="args",
                                required=False,
                                help="Specify the extension of the function "
                                     "files that are asociated with a service"
                                     " validation.")
validations_parser.add_argument("cfile",
                                location="args",
                                required=False,
                                help="Specify a directory to search for "
                                     "file with custom rules definition. "
                                     "Particularly useful when using the "
                                     "'--custom' argument.")
validations_parser.add_argument("source",
                                choices=['url', 'local', 'embedded'],
                                default='local',
                                help="Specify source of the descriptor file. "
                                     "It can take the values 'url' (when the "
                                     "source is a URL), 'local' when the file"
                                     " is file from the local file system and"
                                     " 'embedded' when the descriptor is "
                                     "included as an attachment in the "
                                     "request. In the first two cases a path "
                                     "parameter is required",
                                required=True)

watchers_parser = api_v1.parser()
watchers_parser.add_argument("watch_path",
                             help="Specify the path of the watchers that will "
                                  "will be created.",
                             required=True)
watchers_parser.add_argument("obj_type",
                             choices=['function', 'service', 'project'],
                             help="Specify the type of the validation that "
                                  "will be watched.",
                             required=True)
watchers_parser.add_argument("syntax",
                             location="args",
                             type=inputs.boolean,
                             help="Specify the syntax of the validation that "
                                  "will be watched.",
                             required=False)
watchers_parser.add_argument("integrity",
                             location="args",
                             type=inputs.boolean,
                             help="Specify the integrity of the validation "
                                  "that will be watched.",
                             required=False)
watchers_parser.add_argument("topology",
                             location="args",
                             type=inputs.boolean,
                             help="Specify the topology of the validation "
                                  "that will be watched.",
                             required=False)
watchers_parser.add_argument("custom",
                             location="args",
                             type=inputs.boolean,
                             help="Specify the custom of the validation that "
                                  "will be watched.",
                             required=False)

flushes_parser = api_v1.parser()
flushes_parser.add_argument("type",
                            location="args",
                            choices=['validations', 'resources', 'watchers'],
                            required=True,
                            help="Specify the cache that will be reseted.")


@api_v1.route("/validations/<string:validationId>/topology")
class ValidationGetNetTopology(Resource):
    @api_v1.response(200, "Successfully operation.")
    @api_v1.response(400, "Bad request: Could not get"
                          "the net topology of requested validation.")
    def get(self, validationId):

        vid = get_validation(validationId)
        print(vid)
        if (not vid):
            return ('Validation with id {} does not exist'
                    .format(validationId), 404)
        if (('net_topology' not in vid) or (vid['net_topology'] == '[]')):
            return ('Validation with id {} does not have net_topology '
                    'report'.format(validationId), 404)
        return vid['net_topology']


@api_v1.route("/resources")
class Resources(Resource):

    def get(self):

        resources = cache.get('resources')
        if not resources:
            return ('No resources in cache', 404)
        return resources, 200

    def delete(self):

        log.info('Deleting cached resources.')
        flush_resources()
        return 200


@api_v1.route("/validations/<string:validationId>/fwgraph")
class ValidationGetNetFWGraph(Resource):
    @api_v1.response(200, "Successfully operation.")
    @api_v1.response(400, "Bad request: Could not get"
                          "the fwgraph of requested validation.")
    def get(self, validationId):
        vid = get_validation(validationId)
        print(vid)
        if (not vid):
            return ('Validation with id {} does not exist'
                    .format(validationId), 404)
        if (('net_fwgraph' not in vid) or (vid['net_fwgraph'] == '[]')):
            return ('Validation with id {} does not have net_fwgraph '
                    'report'.format(validationId), 404)
        return vid['net_fwgraph']


@api_v1.route("/validations/<string:validationId>")
class DeleteValidation(Resource):

    def delete(self, validationId):
        vid = get_validation(validationId)
        if (not vid):
            return ('Validation with id {} does not exist'
                    .format(validationId), 404)
        else:
            log.info('Deleting validation {}'.format(validationId))
            validations = cache.get('validations')
            del validations[validationId]
            cache.set('validations', validations)
            return 200

    def get(self, validationId):
        vid = get_validation(validationId)
        if (not vid):
            return ('Validation with id {} does not exist'
                    .format(validationId), 404)
        else:
            return vid, 200


@api_v1.route("/validations")
class Validation(Resource):
    """
    Endpoint for validating descriptors.
    """
    # @api_v1.expect(validations_parser)
    # @api_v1.marshal_with(packages_status_item_get_return_model)
    @api_v1.response(200, "Successfully validation.")
    @api_v1.response(400, "Bad request: Could not validate"
                          "the given descriptor.")
    def delete(self):
        log.info('Deleting cached validations.')
        flush_validations()
        return 200

    def get(self):
        validations = cache.get('validations')
        if not validations:
            return ('No validations in cache', 404)
        return validations, 200

    def post(self, **kwargs):
        args = validations_parser.parse_args()
        log.info("POST to /validation w. args: {}".format(args))
        # flush_validations()
        # flush_resources()
        check_correct_args = check_args(args)
        if check_correct_args == True:
            keypath, path = process_request(args)
            if not keypath or not path:
                return 'Dont find descriptor in this path', 404

            obj_type = check_obj_type(args)
            result = _validate_object(args, path, keypath, obj_type)
            return result
        else:
            return check_correct_args


@api_v1.route("/watchers")
class Watch(Resource):
    @api_v1.response(200, "Successfully operation.")
    @api_v1.response(400, "Bad request.")
    def get(self):
        watchers = cache.get('watchers')
        if not watchers:
            return ('No watchers in cache', 404)
        return watchers, 200

    def post(self, **kwargs):
        args = watchers_parser.parse_args()
        result = install_watchers(args.watch_path,
                                  args.obj_type,
                                  syntax=(args.syntax or False),
                                  integrity=(args.integrity or False),
                                  topology=(args.topology or False),
                                  custom=(args.custom or False))

        return result

    def delete(self):
        log.info('Reseting watchers')
        flush_watchers()
        return 200

def _validate_object(args, path, keypath, obj_type):
    # protect against incorrect parameters

    rid = gen_resource_key(path)
    vid = gen_validation_key(keypath, obj_type, args['syntax'],
                             args['integrity'], args['topology'],
                             args['custom'], args['cfile'] or False)
    resource = get_resource(rid)
    validation = get_validation(vid)
    hashFile = get_file_hash(path)
    if(args['custom'] and args['source'] == 'local'):
        custom_rid = gen_resource_key(args['cfile'])
        custom_hashFile = get_file_hash(args['cfile'])
        custom_resource = get_resource(custom_rid)
    elif(args['custom'] and args['source'] == 'embedded'):
        if 'descriptor' not in request.files:
            log.degub('Miss descriptor file in the request')
            return 'Miss descriptor file in the request', 400
        if 'rules' not in request.files:
            log.degub('Miss rules file in the request')
            return 'Miss rules file in the request', 400
        rules_path = get_file(request.files['rules'])
        print(rules_path)
        custom_rid = gen_resource_key(rules_path)
        custom_hashFile = get_file_hash(rules_path)
        custom_resource = get_resource(custom_rid)

    if resource and validation:
        if(validation['resources']['vnfd']['hashFile'] == hashFile):
            if(args['custom']):
                if(custom_resource):
                    if(validation['resources']['customRules']
                       ['hashFile'] == custom_hashFile):
                        log.info("Returning cached result "
                                 "for '{0}'".format(vid))
                        update_resource_validation(rid, vid)
                        return validation
            else:
                log.info("Returning cached result for '{0}'".format(vid))
                update_resource_validation(rid, vid)
                return validation

    log.info("Starting validation [type={}, path={}, syntax={}, "
             "integrity={}, topology={}, custom={}, "
             "resource_id:={}, validationId={}]"
             .format(obj_type, path, args['syntax'],
                     args['integrity'], args['topology'],
                     args['custom'], rid, vid))
    if (args['custom'] and args['source'] == 'local'):
        set_resource(rid, keypath, obj_type, hashFile, vid)
        set_resource(custom_rid, args['cfile'], 'custom_rule',
                     custom_hashFile, vid)
    else:
        set_resource(rid, keypath, obj_type, hashFile, vid)

    if args['source'] == 'embedded':
        log.info('File embedded in request')
        # Save file passed in the request
        descriptor_path = path
        validator = Validator()
        if not args['custom']:
            validator.configure(syntax=(args['syntax'] or False),
                                integrity=(args['integrity'] or False),
                                topology=(args['topology'] or False),
                                custom=(args['custom'] or False),
                                cfile=(args['cfile'] or False),
                                dext=(args['dext'] or False),
                                dpath=(args['dpath'] or False),
                                workspace_path=(args['workspace']
                                                or False))
        if args['custom']:
            validator.configure(syntax=(args['syntax'] or False),
                                integrity=(args['integrity'] or False),
                                topology=(args['topology'] or False),
                                custom=(args['custom'] or False),
                                cfile=rules_path,
                                dext=(args['dext'] or False),
                                dpath=(args['dpath'] or False),
                                workspace_path=(args['workspace']
                                                or False))

        if args['function']:
            log.info("Validating Function: {}".format(descriptor_path))
            # TODO check if the function is a valid file path
            validator.validate_function(descriptor_path)
    else:
        if (args['source'] == 'local'):
            log.info('Local file')
            path = args['path']
        elif (args['source'] == 'url'):
            log.info('URL file')
            path = get_url(args['path'])

        validator = Validator()
        validator.configure(syntax=(args['syntax'] or False),
                            integrity=(args['integrity'] or False),
                            topology=(args['topology'] or False),
                            custom=(args['custom'] or False),
                            cfile=(args['cfile'] or False),
                            dext=(args['dext'] or False),
                            dpath=(args['dpath'] or False),
                            workspace_path=(args['workspace'] or False))

        if args['function']:
            log.info("Validating Function: {}".format(path))
            # TODO check if the function is a valid file path
            validator.validate_function(path)

        elif args['service']:
            log.info("Validating Service: {}".format(path))
            # TODO check if the function is a valid file path
            validator.validate_service(path)

        elif args['project']:
            log.info("Validating Project: {}".format(path))
            # TODO check if the function is a valid file path
            validator.validate_project(path)

    json_result = gen_report_result(vid, validator)
    net_topology = gen_report_net_topology(validator)
    net_fwgraph = gen_report_net_fwgraph(validator)
    if(args['custom']):
        set_validation(vid, rid, path, obj_type, args['syntax'],
                       args['integrity'], args['topology'], args['custom'],
                       hashFile, custom_rid, custom_hashFile,
                       result=json_result, net_topology=net_topology,
                       net_fwgraph=net_fwgraph)
    else:
        set_validation(vid, rid, path, obj_type, args['syntax'],
                       args['integrity'], args['topology'], args['custom'],
                       hashFile, result=json_result, net_topology=net_topology,
                       net_fwgraph=net_fwgraph)
    update_resource_validation(rid, vid)
    validation_to_return = get_validation(vid)
    # return json_result
    return validation_to_return, 200


def install_watchers(watch_path, obj_type, syntax, integrity, topology,
                     custom):
    log.info("Setting watchers for {0} validation on path: {1}"
             .format(obj_type, watch_path))
    if os.path.isdir(watch_path):
        Validatewatchers(watch_path, _validate_object_from_watch)
        set_watch(watch_path, obj_type, syntax, integrity, topology, custom)
        return 'Dir watchers cached', 200
    elif os.path.isfile(watch_path):
        filename = os.path.basename(watch_path)
        dirname = os.path.dirname(watch_path)
        Validatewatchers(dirname, _validate_object_from_watch,
                         filename=filename)
        set_watch(watch_path, obj_type, syntax, integrity, topology, custom)
        return 'File watchers cached', 200
    else:
        return 'Incorrect path for be watched', 400


def load_watch_dirs(workspace):
    if not workspace:
        return

    log.info("Loading validator watcherss")

    for watch_path, watch in workspace.validate_watchers.items():
        if watch_exists(watch_path):
            log.warning("watchers path '{0}' does not exist. Ignoring."
                        .format(watch_path))
            continue

        log.debug("Loading validator watchers: {0}".format(watch_path))

        assert (watch['type'] == 'project' or watch['type'] == 'package' or
                watch['type'] == 'service' or watch['type'] == 'function')

        if 'cfile' not in watch:
            watch['cfile'] = None
        if 'dpath' not in watch:
            watch['dpath'] = None
        if 'dext' not in watch:
            watch['dext'] = None
        if 'workspace' not in watch:
            watch['workspace'] = None
        install_watchers(watch_path, watch['type'], watch['syntax'],
                         watch['integrity'], watch['topology'],
                         watch['custom'])

        _validate_object_watcher(watch, watch_path, watch_path, watch['type'])


def _validate_object_watcher(args, path, keypath, obj_type):
    # protect against incorrect parameters

    rid = gen_resource_key(path)
    vid = gen_validation_key(keypath, obj_type, args['syntax'],
                             args['integrity'], args['topology'],
                             args['custom'], args['cfile'] or False)
    resource = get_resource(rid)
    validation = get_validation(vid)
    hashFile = get_file_hash(path)
    if(args['custom']):
        custom_rid = gen_resource_key(args['cfile'])
        custom_hashFile = get_file_hash(args['cfile'])
        custom_resource = get_resource(custom_rid)

    if resource and validation:
        if(validation['resources']['vnfd']['hashFile'] == hashFile):
            if(args['custom']):
                if(custom_resource):
                    if(validation['resources']['customRules']
                       ['hashFile'] == custom_hashFile):
                        log.info("Returning cached result "
                                 "for '{0}'".format(vid))
                        update_resource_validation(rid, vid)
                        return validation
            else:
                log.info("Returning cached result for '{0}'".format(vid))
                update_resource_validation(rid, vid)
                return validation

    log.info("Starting validation [type={}, path={}, syntax={}, "
             "integrity={}, topology={}, custom={}, "
             "resource_id:={}, validationId={}]"
             .format(obj_type, path, args['syntax'],
                     args['integrity'], args['topology'],
                     args['custom'], rid, vid))
    if args['custom']:
        set_resource(rid, keypath, obj_type, hashFile, vid)
        set_resource(custom_rid, args['cfile'], 'custom_rule',
                     custom_hashFile, vid)
    else:
        set_resource(rid, keypath, obj_type, hashFile, vid)

    validator = Validator()
    validator.configure(syntax=(args['syntax'] or False),
                        integrity=(args['integrity'] or False),
                        topology=(args['topology'] or False),
                        custom=(args['custom'] or False),
                        cfile=(args['cfile'] or False),
                        dext=(args['dext'] or False),
                        dpath=(args['dpath'] or False),
                        workspace_path=(args['workspace'] or False))

    if obj_type == 'function':
        log.info("Validating Function: {}".format(path))
        # TODO check if the function is a valid file path
        validator.validate_function(path)

    elif obj_type == 'service':
        log.info("Validating Service: {}".format(path))
        # TODO check if the function is a valid file path
        validator.validate_service(path)

    elif obj_type == 'project':
        log.info("Validating Project: {}".format(path))
        # TODO check if the function is a valid file path
        validator.validate_project(path)

    json_result = gen_report_result(vid, validator)
    net_topology = gen_report_net_topology(validator)
    net_fwgraph = gen_report_net_fwgraph(validator)
    if(args['custom']):
        set_validation(vid, rid, path, obj_type, args['syntax'],
                       args['integrity'], args['topology'], args['custom'],
                       hashFile, custom_rid, custom_hashFile,
                       result=json_result, net_topology=net_topology,
                       net_fwgraph=net_fwgraph)
    else:
        set_validation(vid, rid, path, obj_type, args['syntax'],
                       args['integrity'], args['topology'], args['custom'],
                       hashFile, result=json_result, net_topology=net_topology,
                       net_fwgraph=net_fwgraph)
    update_resource_validation(rid, vid)

    # return json_result
    return {"validation_process_uuid": "test",
            "status": 200,
            "error_count": validator.error_count,
            "errors": validator.errors}


def set_watch(path, obj_type, syntax, integrity, topology, custom):
    log.debug("Caching watch '{0}".format(path))
    watchers = cache.get('watchers')

    if not watchers:
        watchers = dict()

    if not watch_exists(path):
        watchers[path] = dict()

    watchers[path]['type'] = obj_type
    watchers[path]['syntax'] = syntax
    watchers[path]['integrity'] = integrity
    watchers[path]['topology'] = topology
    watchers[path]['custom'] = custom

    cache.set('watchers', watchers)


def watch_exists(path):
    if not cache.get('watchers'):
        return False
    return path in cache.get('watchers').keys()


def get_watch(path):
    if not watch_exists(path):
        return
    return cache.get('watchers')[path]


def _validate_object_from_watch(path):
    log.info(path)
    if not watch_exists(path):
        log.error("Invalid cached watch. Cannot proceed with validation")
        return

    watch = get_watch(path)
    log.info("Validating {0} from watch: {1}".format(watch['type'], path))
    # result = _validate_object(watch, path, path, watch['type'])
    rid = gen_resource_key(path)
    vid = gen_validation_key(path, watch['type'], watch['syntax'],
                             watch['integrity'], watch['topology'],
                             watch['custom'])
    resource = get_resource(rid)
    hashFile = get_file_hash(path)
    validation = get_validation(vid)
    if resource and validation:
        if(resource['hashFile'] == hashFile):
            log.info("Returning cached result for '{0}'".format(vid))
            update_resource_validation(rid, vid)
            result = validation
    else:
        log.info("Starting validation [type={}, path={}, syntax={}, "
                 "integrity={}, topology={}, custom={}, "
                 "resource_id:={}, validationId={}]"
                 .format(watch['type'], path, watch['syntax'],
                         watch['integrity'], watch['topology'],
                         watch['custom'], rid, vid))

        set_resource(rid, path, 'function', hashFile, vid)
        validator = Validator()
        validator.configure(syntax=(watch['syntax'] or False),
                            integrity=(watch['integrity'] or False),
                            topology=(watch['topology'] or False),
                            custom=(watch['custom'] or False))

        if watch['type'] == 'function':
            log.info("Validating Function: {}".format(path))
            # TODO check if the function is a valid file path
            validator.validate_function(path)

        elif watch['type'] == 'service':
            log.info("Validating Service: {}".format(path))
            # TODO check if the function is a valid file path
            validator.validate_service(path)

        elif watch['type'] == 'project':
            log.info("Validating Project: {}".format(path))
            # TODO check if the function is a valid file path
            validator.validate_project(path)

        json_result = gen_report_result(rid, validator)
        net_topology = gen_report_net_topology(validator)
        net_fwgraph = gen_report_net_fwgraph(validator)

        set_validation(vid, rid, path, watch['type'], watch['syntax'],
                       watch['integrity'], watch['topology'], watch['custom'],
                       hashFile, result=json_result,
                       net_topology=net_topology, net_fwgraph=net_fwgraph)
        update_resource_validation(rid, vid)

        result = {"validation_process_uuid": "test",
                  "status": 200,
                  "error_count": validator.error_count,
                  "errors": validator.errors}

    # re-schedule watchers
    install_watchers(path, watch['type'], watch['syntax'], watch['integrity'],
                     watch['topology'], watch['custom'])

    if not result:
        return
    log.info(result)


def gen_watchers():
    # retrieve dictionary of watched resources, in the format:
    # path: { type | syntax | integrity | topology }
    report = dict()
    watchers = cache.get('watchers')
    if not watchers:
        return '', 204
    for path, watch in watchers.items():
        report[path] = dict()
        report[path]['type'] = watch['type']
        report[path]['syntax'] = watch['syntax']
        report[path]['integrity'] = watch['integrity']
        report[path]['topology'] = watch['topology']

    return json.dumps(report)

#
# def cached_validation_to_dict(str):
#     list_dict_str = str.split()
#     dict_str = ''.join(list_dict_str)
#     dict = ast.literal_eval(dict_str)
#     return dict
#


def flush_validations():
    cache.set('validations', dict())
    return 'ok', 200


def flush_watchers():
    cache.set('watchers', dict())
    return 'ok', 200


def flush_resources():
    cache.set('resources', dict())
    return 'ok', 200


def gen_report_result(validationId, validator):

    print("building result report for {0}".format(validationId))
    report = dict()
    report['validationId'] = '/validations/' + validationId
    report['error_count'] = validator.error_count
    report['warning_count'] = validator.warning_count

    if validator.error_count:
        report['errors'] = validator.errors
    if validator.warning_count:
        report['warnings'] = validator.warnings
    return report


def gen_report_net_topology(validator):

    print(validator.storage.services.items())
    report = list()
    for sid, service in validator.storage.services.items():
        graph_repr = ''
        if not service.complete_graph:
            return
        for line in service.complete_graph:
            if not line:
                continue
            graph_repr += line
        report.append(graph_repr)

    # TODO: temp patch for returning only the topology of the first service
    if len(report) > 0:
        report = report[0]
        return report

    return report


def gen_report_net_fwgraph(validator):
    print("building result report net fwgraph")
    report = list()
    for sid, service in validator.storage.services.items():
        report.append(service.fw_graphs)

    # TODO: temp patch for returning only the fwgraph of the first service
    if len(report) > 0:
        report = report[0]

    return report


def set_resource(rid, path, obj_type, hashFile, vid_related):

    log.info("Caching resource {0}".format(rid))
    resources = cache.get('resources')
    if not resources:
        resources = dict()

    if not resource_exists(rid):
        resources[rid] = dict()

    resources[rid]['path'] = path
    resources[rid]['type'] = obj_type
    resources[rid]['hashFile'] = hashFile
    if 'validations' in resources[rid]:
        resources[rid]['validations'].append('/validations/' + vid_related)
    else:
        resources[rid]['validations'] = []
        resources[rid]['validations'].append('/validations/' + vid_related)
    log.info(resources[rid])
    cache.set('resources', resources)


def get_file_hash(path):
    hashFile = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashFile.update(chunk)
    return hashFile.hexdigest()


def get_resource(rid):
    if not resource_exists(rid):
        return
    return cache.get('resources')[rid]


def set_validation(vid, rid, path, obj_type, syntax, integrity, topology,
                   custom, hashFile, custom_rid=None,
                   custom_hashFile=None, result=None, net_topology=None,
                   net_fwgraph=None):

    log.info("Caching validation '{0}'".format(vid))
    validations = cache.get('validations')
    if not validations:
        validations = dict()

    if vid not in validations.keys():
        validations[vid] = dict()

    validations[vid]['path'] = path
    validations[vid]['type'] = obj_type
    validations[vid]['syntax'] = syntax or False
    validations[vid]['integrity'] = integrity or False
    validations[vid]['topology'] = topology or False
    validations[vid]['custom'] = custom or False
    validations[vid]['resources'] = dict()
    validations[vid]['resources']['vnfd'] = {'id': '/resources/' + rid,
                                             'hashFile': hashFile}
    if custom_rid:
        validations[vid]['resources']['customRules'] = (
            {'id': '/resources/' + custom_rid,
             'hashFile': custom_hashFile})
    if result:
        validations[vid]['result'] = result
    if net_topology:
        validations[vid]['net_topology'] = net_topology
    if net_fwgraph:
        validations[vid]['net_fwgraph'] = net_fwgraph

    cache.set('validations', validations)


def get_validation(vid):
    if not validation_exists(vid):
        return
    return cache.get('validations')[vid]


def get_resources():

    # resource_id {type | path | syntax | integrity | topology}
    report = dict()
    resources = cache.get('resources')
    validations = cache.get('validations')

    if not resources or not validations:
        return '', 204

    for rid, resource in resources.items():

        report[rid] = dict()
        report[rid]['type'] = resource['type']
        report[rid]['path'] = resource['path']
        report[rid]['syntax'] = resource['syntax']
        report[rid]['integrity'] = resource['integrity']
        report[rid]['topology'] = resource['topology']

    return json.dumps(report, sort_keys=true,
                      indent=4, separators=(',', ': ')).encode('utf-8')


def check_obj_type(args):
    if (args.function):
        return 'function'
    elif (args.service):
        return 'service'
    elif (args.project):
        return 'project'


def gen_validation_key(path, otype, s, i, t, c, cfile=None):
    val_hash = hashlib.md5()
    val_hash.update(path.encode('utf-8'))
    val_hash.update(otype.encode('utf-8'))
    if s:
        val_hash.update('syntax'.encode('utf-8'))
    if i:
        val_hash.update('integrity'.encode('utf-8'))
    if t:
        val_hash.update('topology'.encode('utf-8'))
    if c:
        val_hash.update('custom'.encode('utf-8'))
    if cfile:
        val_hash.update(cfile.encode('utf-8'))
    return val_hash.hexdigest()


def update_resource_validation(rid, vid):
    if not validation_exists(vid):
        log.error("Internal error: failed to update resource")
        return

    if not resource_exists(rid):
        return

    log.debug("Updating resource '{0}' to: '{1}'".format(rid, vid))
    resources = cache.get('resources')
    resources[rid]['latest_vid'] = vid
    cache.set('resources', resources)


def resource_exists(rid):
    if not cache.get('resources'):
        return False
    return rid in cache.get('resources').keys()


def validation_exists(vid):
    if not cache.get('validations'):
        return False
    return vid in cache.get('validations').keys()


def gen_resource_key(path):
    # assert (type(path) == str and type(otype) == str)

    res_hash = hashlib.md5()
    # res_hash.update(path.encode('utf-8'))
    # res_hash.update(otype.encode('utf-8'))
    # if s:
    #     print('sintaxe')
    #     res_hash.update('syntax'.encode('utf-8'))
    # if i:
    #     print('integrity')
    #     res_hash.update('integrity'.encode('utf-8'))
    # if t:
    #     print('topology')
    #     res_hash.update('topology'.encode('utf-8'))
    # if c:
    #     print('custom')
    #     res_hash.update('custom'.encode('utf-8'))
    #
    # print(res_hash.hexdigest())
    # generate path hash
    res_hash.update(str(generate_hash(os.path.abspath(path)))
                    .encode('utf-8'))
    # validation event config must also be included
    res_hash.update(repr(sorted(EventLogger.load_eventcfg().items()))
                    .encode('utf-8'))
    return res_hash.hexdigest()


def process_request(args):
    source = args.source
    if source == 'local' and args.path:
        keypath = args.path
        path = get_local(args.path)
        if not path:
            return None, None

    elif source == 'url' and args.path:
        keypath = request.form['path']
        path = get_url(request.form['path'])

    elif source == 'embedded' and 'descriptor' in request.files:
        keypath = secure_filename(request.files['descriptor'].filename)
        path = get_file(request.files['descriptor'])

    else:
        req_errors.append('Invalid source, path or file parameters')
        return None, None

    return keypath, path


def get_local(path):
    artifact_root = add_artifact_root()
    if os.path.isfile(path):
        filepath = os.path.join(artifact_root, os.path.basename(path))
        log.debug("Copying local file: '{0}'".format(filepath))
        shutil.copyfile(path, filepath)
        set_artifact(filepath)

    elif os.path.isdir(path):
        dirname = os.path.basename(os.path.abspath(path))
        filepath = os.path.join(artifact_root, dirname)
        log.debug("Copying local tree: '{0}'".format(filepath))
        shutil.copytree(path, filepath)
        set_artifact(filepath)
        for root, dirs, files in os.walk(filepath):
            for d in dirs:
                set_artifact(os.path.join(root, d))
            for f in files:
                set_artifact(os.path.join(root, f))
    else:
        req_errors.append("Invalid local path: '{0}'".format(path))
        log.error("Invalid local path: '{0}'".format(path))
        return

    return filepath


def check_args(args):

    if (args.syntax is None and args.integrity is None
            and args.topology is None):
        log.info('Need to specify at least one type of validation')
        return {"error_message": "Missing validation"}, 400
    if (args.function is None and args.service is None
            and args.project is None):
        log.info('Need to specify the type of the descriptor that will ' +
                 'be validated (function, service, project)')
        return {"error_message": "Missing service, function " +
                "and project parameters"}, 400

    if (args.function and args.service):
        log.info("Not possible to validate function and service in the" +
                 " same request")
        return {"error_message": "Not possible to validate function" +
                " and service and project in the same request"}, 400

    if (args.function and args.project):
        log.info("Not possible to validate function and project in the" +
                 " same request")
        return {"error_message": "Not possible to validate function" +
                " and project in the same request"}, 400

    if (args.service and args.project):
        log.info("Not possible to validate service and project in the" +
                 " same request")
        return {"error_message": "Not possible to validate service" +
                " and project in the same request"}, 400

    if (args.source == 'local' or args.source == 'url'):
        if (args.path is None):
            log.info('With local or url source the path of this ' +
                     'source should be specified')
            return {"error_message": "File path need it when local or " +
                    "url source are used"}, 400

    if (args.service and
            (args.integrity or args.topology or args.custom)):
        if (args.dpath is None or args.dext is None):
            log.info('With integrity or topology validation of a service' +
                     ' we need to specify the path of the functions ' +
                     '(dpath) and the extension of it (dext)')
            return {"error_message": "Need functions path " +
                    "(dpath) and the extension of it (dext) to validate " +
                    "service integrity|topology|custom_rules"}, 400

    if (args.custom and args.source == 'local'):
        if (args.cfile is None):
            log.info('With custom rules validation the path of ' +
                     'the file with the rules should be specified ' +
                     '(cfile)')
            return {"error_message": "Need rules file path" +
                    " (cfile) to validate custom rules of " +
                    "descriptor"}, 400
    if (args.project):
        if (args.workspace is None):
            log.info('With project validation the workspace path ' +
                     'of the project should be specified (workspace)')
            return {"error_message": "Need workspace path " +
                    "(workspace) to validate project"}, 400
    return True


def get_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(add_artifact_root(), filename)
    file.save(filepath)
    set_artifact(filepath)
    return filepath


def add_artifact_root():
    artifact_root = os.path.join(app.config['ARTIFACTS_DIR'],
                                 str(time.time() * 1000))
    os.makedirs(artifact_root, exist_ok=False)
    set_artifact(artifact_root)
    return artifact_root


def set_artifact(artifact_path):
    log.debug("Caching artifact '{0}'".format(artifact_path))
    artifacts = cache.get('artifacts')
    if not artifacts:
        artifacts = list()
    artifacts.append(artifact_path)
    cache.set('artifacts', artifacts)


def get_url(url):
    u = urllib2.urlopen(url)
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filepath = os.path.join(add_artifact_root(), os.path.basename(path))

    with open(filepath, 'wb') as f:
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            f.write(buffer)

    set_artifact(filepath)
    return filepath


def generate_hash(f, cs=128):
    return __generate_hash__(f, cs) \
        if os.path.isfile(f) \
        else __generate_hash_path__(f, cs)


def __generate_hash__(f, cs=128):
    hash = hashlib.md5()
    with open(f, "rb") as file:
        for chunk in iter(lambda: file.read(cs), b''):
            hash.update(chunk)
    return hash.hexdigest()


def __generate_hash_path__(p, cs=128):
    hashes = []
    for root, dirs, files in os.walk(p):
        for f in sorted(files):  # guarantee same order to obtain same hash
            hashes.append(__generate_hash__(os.path.join(root, f), cs))
        for d in sorted(dirs):  # guarantee same order to obtain same hash
            hashes.append(__generate_hash_path__(os.path.join(root, d), cs))
        break
    return _reduce_hash(hashes)


def _reduce_hash(hashlist):
    hash = hashlib.md5()
    for hashvalue in sorted(hashlist):
        hash.update(hashvalue.encode('utf-8'))
    return hash.hexdigest()


@api_v1.route("/pings")
class Ping(Resource):

    # @api_v1.marshal_with(ping_get_return_model)
    @api_v1.response(200, "OK")
    def get(self):
        return 'OK', 200
