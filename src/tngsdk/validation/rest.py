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
import tempfile
from flask import Flask, Blueprint
from flask_restplus import Resource, Api, Namespace
from flask_restplus import fields, inputs
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import requests
from requests.exceptions import RequestException
from flask_cors import CORS
from flask_cache import Cache


from tngsdk.validation import cli
from tngsdk.validation.validator import Validator

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
# comment DANI
# if app.config['CACHE_TYPE'] == 'redis':
#
#     redis_auth = app.config['REDIS_USER'] + ':' + app.config[
#         'REDIS_PASSWD'] + '@' \
#         if app.config['REDIS_USER'] and app.config['REDIS_PASSWD'] else ''
#     redis_url = 'redis://' + redis_auth + app.config['REDIS_HOST'] + \
#                 ':' + app.config['REDIS_PORT']
#
#     cache = Cache(app, config={'CACHE_TYPE': 'redis',
#                                 'CACHE_DEFAULT_TIMEOUT': 0,
#                                 'CACHE_REDIS_URL': redis_url})
#
# elif app.config['CACHE_TYPE'] == 'simple':
#      cache = Cache(app, config={'CACHE_TYPE': 'simple',
#                                 'CACHE_DEFAULT_TIMEOUT': 0})
#
# else:
#      print("Invalid cache type.")
#      sys.exit(1)
# Comment DANI

# keep temporary request errors
# req_errors = []

# class ValidateWatcher(FileSystemEventHandler):
#     def __init__(self, path, callback, filename=None):
#         self.path = path
#         self.filename = filename
#         self.callback = callback
#         self.observer = Observer()
#         self.observer.schedule(self, self.path,
#                                recursive=False if self.filename else True)
#         self.observer.start()
#         # self.observer.join()

#     def on_modified(self, event):
#         print(self.filename)
#         print(event.src_path)
#         print(event)

#         self.observer.stop()
#         self.callback(self.path)


# def initialize(debug=False):
#     log.info("Initializing validator service")

#     try:
#         cache.clear()
#     except:
#         sys.exit(1)

#     cache.add('debug', debug)
#     cache.add('artifacts', list())
#     cache.add('validations', dict())
#     cache.add('resources', dict())
#     cache.add('latest', dict())
#     cache.add('watches', dict())

#     os.makedirs(app.config['ARTIFACTS_DIR'], exist_ok=True)
#     set_artifact(app.config['ARTIFACTS_DIR'])

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
                                required=True
)

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
    def post(self, **kwargs):
        args = validations_parser.parse_args()

        log.info("POST to /validation w. args: {}".format(args))

        if ((args['function'] is not None) and (args['service']is not None)):
            return {"error_message": "Not possible to validate " +
                    "service and function in the same request"}, 400

        if ((args['function'] is None) and (args['service']is None)):
            return {"error_message": "Missing service and" +
                    " function parameters"}, 400

        # TO BE REMOVED when asynchronous processing is implemented
        if not args['sync']:
            return {"error_message": "Asynchronous processing " +
                    "not yet implemented"}, 400

        validator = Validator()
        # None or False = False / True or False = True / False or False = False
        validator.configure(syntax=(args['syntax'] or False),
                            integrity=(args['integrity'] or False),
                            topology=(args['topology'] or False),
                            dpath=(args['dpath'] or False))

        if args['function'] is not None:
            log.info("Validating Function: {}".format(args['function']))
            # TODO check if the function is a valid file path
            validator.validate_function(args.function)

        elif args['service'] is not None:
            log.info("Validating Service: {}".format(args['service']))
            # TODO check if the function is a valid file path
            validator.validate_service(args.service)

        # TODO try to capture exceptions and errors

        # TODO store results in redis so that the result can be checked

        return {"validation_process_uuid": "test",
                "status": 200,
                "error_count": validator.error_count,
                "errors": validator.errors}

req_errors = []

@app.route('/validate/project', methods=['POST'])
def validate_project():
    return _validate_object_from_request('project')


@app.route('/validate/service', methods=['POST'])
def validate_service():
    return _validate_object_from_request('service')


@app.route('/validate/function', methods=['POST'])
def validate_function():
    return _validate_object_from_request('function')


def _validate_object_from_request(object_type):

    assert object_type == 'project' or object_type == 'package' or \
           object_type == 'service' or object_type == 'function'

    keypath, path = process_request()
    if not keypath or not path:
        return render_errors(), 400

    return _validate_object(keypath, path, object_type, args.syntax,
                            args.integrity, args.topology)


def validate_parameters(obj_type, syntax, integrity, topology):
    assert (obj_type == 'project' or obj_type == 'package' or
           obj_type == 'service' or obj_type == 'function')

    if obj_type == 'service' and (integrity or topology):
        return ("Invalid parameters: cannot validate integrity and/or "
               "topology of a standalone service")


def _validate_object(keypath, path, obj_type, syntax, integrity, topology):
    # protect against incorrect parameters
    perrors = validate_parameters(obj_type, syntax, integrity, topology)
    if perrors:
        return perrors, 400

    # rid = gen_resource_key(keypath, obj_type, syntax, integrity, topology)
    # vid = gen_validation_key(path)
    #
    # resource = get_resource(rid)
    # validation = get_validation(vid)
    #
    # if resource and validation:
    #     log.info("Returning cached result for '{0}'".format(vid))
    #     update_resource_validation(rid, vid)
    #     return validation['result']

    log.info("Starting validation [type={}, path={}, flags={}"
             .format(obj_type, path, get_flags(syntax, integrity,
             topology)))

    # set_resource(rid, keypath, obj_type, syntax, integrity, topology)

    validator = Validator()
    validator.configure(syntax, integrity, topology, debug=app.config['DEBUG'],
                        pkg_signature=pkg_signature, pkg_pubkey=pkg_pubkey)
    # remove default dpath
    validator.dpath = None
    val_function = getattr(validator, 'validate_' + obj_type)

    result = val_function(path)
    print_result(validator, result)
    # json_result = gen_report_result(rid, validator)
    # net_topology = gen_report_net_topology(validator)
    # net_fwgraph = gen_report_net_fwgraph(validator)
    #
    # set_validation(vid, result=json_result, net_topology=net_topology,
    #                net_fwgraph=net_fwgraph)
    # update_resource_validation(rid, vid)
    #
    # return json_result



def process_request():
    args = validations_parser.parse_args()
    if args.source == 'local' and args.path:
        keypath = args.path
        path = get_local(args.path)
        if not path:
            return None, None

    elif source == 'url' and 'path' in request.form:
        keypath = args.path
        path = get_url(args.path)

    elif source == 'embedded' and 'file' in request.files:
        keypath = secure_filename(request.files['file'].filename)
        path = get_file(request.files['file'])

    else:
        req_errors.append('Invalid source, path or file parameters')
        return None, None

    return keypath, path


def add_artifact_root():
    artifact_root = os.path.join(app.config['ARTIFACTS_DIR'],
                                 str(time.time() * 1000))
    os.makedirs(artifact_root, exist_ok=False)
    # set_artifact(artifact_root)
    return artifact_root


# def set_artifact(artifact_path):
#     log.debug("Caching artifact '{0}'".format(artifact_path))
#     artifacts = cache.get('artifacts')
#     if not artifacts:
#         artifacts = list()
#     artifacts.append(artifact_path)
#     cache.set('artifacts', artifacts)


def get_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(add_artifact_root(), filename)
    file.save(filepath)
    # set_artifact(filepath)
    return filepath


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

    # set_artifact(filepath)
    return filepath


def get_local(path):
    artifact_root = add_artifact_root()
    if os.path.isfile(path):
        filepath = os.path.join(artifact_root, os.path.basename(path))
        # log.debug("Copying local file: '{0}'".format(filepath))
        # shutil.copyfile(path, filepath)
        # set_artifact(filepath)

    elif os.path.isdir(path):
        dirname = os.path.basename(os.path.abspath(path))
        filepath = os.path.join(artifact_root, dirname)
        # log.debug("Copying local tree: '{0}'".format(filepath))
        # shutil.copytree(path, filepath)
        # set_artifact(filepath)
        # for root, dirs, files in os.walk(filepath):
        #     for d in dirs:
        #         set_artifact(os.path.join(root, d))
        #     for f in files:
        #         set_artifact(os.path.join(root, f))
    else:
        req_errors.append("Invalid local path: '{0}'".format(path))
        log.error("Invalid local path: '{0}'".format(path))
        return

    return filepath


def get_flags(syntax, integrity, topology):
    return ('s' if syntax else '' +
            'i' if integrity else '' +
            't' if topology else '')


def render_errors():
    error_str = ''
    for error in req_errors:
        error_str += error + '\n'
    req_errors.clear()
    return error_str




@api_v1.route("/ping")
class Ping(Resource):

    @api_v1.marshal_with(ping_get_return_model)
    @api_v1.response(200, "OK")
    def get(self):
        ut = None
        try:
            ut = str(subprocess.check_output("uptime")).strip()
        except BaseException as e:
            log.warning(str(e))
        return {"ping": "pong",
                "uptime": ut}
