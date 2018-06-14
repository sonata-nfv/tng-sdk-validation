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
# Neither the name of the SONATA-NFV, 5GTANGO, UBIWHERE, Paderborn University
# nor the names of its contributors may be used to endorse or promote
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
import requests
from requests.exceptions import RequestException
from tngsdk.package.packager import PM
from tngsdk.package.storage import TangoCatalogBackend

# To implement watchdogs to subscribe to changes in any descriptor file
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG = logging.getLogger(os.path.basename(__file__))


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
blueprint = Blueprint('api', __name__, url_prefix="/api")
api_v1 = Namespace("v1", description="tng-package API v1")
api = Api(blueprint,
          version="0.1",
          title='5GTANGO tng-sdk-validation API',
          description="5GTANGO tng-package REST API " +
          "to validate descriptors.")
app.register_blueprint(blueprint)
api.add_namespace(api_v1)

##This file should be generated with Swagger form an OpenAPI file, shouldn't it?

#Define Redis username and pass

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

class ValidateWatcher(FileSystemEventHandler):
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
        self.callback(self.path)


def initialize(debug=False):
    log.info("Initializing validator service")

    try:
        cache.clear()
    except:
        sys.exit(1)

    cache.add('debug', debug)
    cache.add('artifacts', list())
    cache.add('validations', dict())
    cache.add('resources', dict())
    cache.add('latest', dict())
    cache.add('watches', dict())

    os.makedirs(app.config['ARTIFACTS_DIR'], exist_ok=True)
    set_artifact(app.config['ARTIFACTS_DIR'])

