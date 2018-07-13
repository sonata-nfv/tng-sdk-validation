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
import tempfile
from flask import Flask, Blueprint, request
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
validations_parser.add_argument("workspace",
                                location="args",
                                required=False,
                                help="Specify the directory of the SDK " +
                                     "workspace for validating the " +
                                     " SDK project." )
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

        check_correct_args = check_args(args)
        if check_correct_args != True:
            return check_correct_args


        if args.source:
            log.info('File embedded in request')
            if 'descriptor' not in request.files:
                log.degub('Miss descriptor file in the request')
                if args.custom:
                    if 'rules' not in request.files:
                        log.degub('Miss rules file in the request')
            else:
                # Save file passed in the request
                descriptor_path = get_file(request.files['descriptor'])

                validator = Validator()
                if not args.custom:
                # None or False = False / True or False = True / False or False = False
                    validator.configure(syntax=(args['syntax'] or False),
                                        integrity=(args['integrity'] or False),
                                        topology=(args['topology'] or False),
                                        custom=(args['custom'] or False),
                                        cfile=(args['cfile'] or False),
                                        dext=(args['dext'] or False),
                                        dpath=(args['dpath'] or False),
                                        workspace_path=(args['workspace'] or False))
                if args.custom:
                    rules_path = get_file(request.files['rules'])
                    validator.configure(syntax=(args['syntax'] or False),
                                        integrity=(args['integrity'] or False),
                                        topology=(args['topology'] or False),
                                        custom=(args['custom'] or False),
                                        cfile=rules_path,
                                        dext=(args['dext'] or False),
                                        dpath=(args['dpath'] or False),
                                        workspace_path=(args['workspace'] or False))

                if args['function'] == True:
                    log.info("Validating Function: {}".format(descriptor_path))
                    # TODO check if the function is a valid file path
                    validator.validate_function(descriptor_path)
        else:
            validator = Validator()
            # None or False = False / True or False = True / False or False = False
            validator.configure(syntax=(args['syntax'] or False),
                                integrity=(args['integrity'] or False),
                                topology=(args['topology'] or False),
                                custom=(args['custom'] or False),
                                cfile=(args['cfile'] or False),
                                dext=(args['dext'] or False),
                                dpath=(args['dpath'] or False),
                                workspace_path=(args['workspace'] or False))

            if args['function'] == True:
                log.info("Validating Function: {}".format(args['path']))
                # TODO check if the function is a valid file path
                validator.validate_function(args.path)

            elif args['service'] == True:
                log.info("Validating Service: {}".format(args['path']))
                # TODO check if the function is a valid file path
                validator.validate_service(args.path)

            elif args['project'] == True:
                log.info("Validating Project: {}".format(args['path']))
                # TODO check if the function is a valid file path
                validator.validate_project(args.path)


            # TODO try to capture exceptions and errors

            # TODO store results in redis so that the result can be checked

            return {"validation_process_uuid": "test",
                    "status": 200,
                    "error_count": validator.error_count,
                    "errors": validator.errors}


def check_args(args):

    if (args.function == None and args.service == None
        and args.project == None):
        log.info('Need to specify the type of the descriptor that will ' +
                 'be validated (function, service, project)')
        return {"error_message": "Missing service, function " +
                "and project parameters"}, 400

    if (args.function == True and args.service == True):
        log.info("Not possible to validate function and service in the" +
                " same request")
        return {"error_message": "Not possible to validate function" +
                " and service and project in the same request"}, 400

    if (args.function == True and args.project == True):
        log.info("Not possible to validate function and project in the" +
                " same request")
        return {"error_message": "Not possible to validate function" +
                " and project in the same request"}, 400

    if (args.service == True and args.project == True):
        log.info("Not possible to validate service and project in the" +
                " same request")
        return {"error_message": "Not possible to validate service" +
                " and project in the same request"}, 400

    if (args.source == 'local' or args.source == 'url'):
        if (args.path == None):
            log.info('With local or url source the path of this ' +
                     'source should be specified')
            return {"error_message": "File path need it when local or " +
                    "url source are used"}, 400

    if (args.service == True and
        (args.integrity == True or args.topology == True
         or args.custom == True)):
        if (args.dpath == None or args.dext == None):
            log.info('With integrity or topology validation of a service' +
                     ' we need to specify the path of the functions ' +
                     '(dpath) and the extension of it (dext)')
            return {"error_message": "Need functions path " +
                    "(dpath) and the extension of it (dext) to validate " +
                    "service integrity|topology|custom_rules"}, 400

    if (args.custom == True and args.custom == 'local'):
        if (args.cfile == None):
            log.info('With custom rules validation the path of ' +
                     'the file with the rules should be specified ' +
                     '(cfile)')
            return {"error_message": "Need rules file path" +
                    " (cfile) to validate custom rules of " +
                    "descriptor"}, 400
    if (args.project == True):
        if (args.workspace == None):
            log.info('With project validation the workspace path ' +
                     'of the project should be specified (workspace)')
            return {"error_message": "Need workspace path " +
                    "(workspace) to validate project "}, 400
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
    artifacts = list()
    artifacts.append(artifact_path)


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
