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


import unittest
import json
import time
import ast
import requests
from requests_toolbelt import MultipartEncoder
from unittest.mock import patch
from requests.exceptions import RequestException
# Do unit test of specific functions
# from tngsdk.validation.rest import app, on_unpackaging_done,
#                                    on_packaging_done
from tngsdk.validation.rest import app

SAMPLES_DIR = 'src/tngsdk/validation/tests/'


# class MockResponse(object):
#         pass

#
# def mock_requests_post(url, json):
#     if url != "https://test.local:8000/cb":
#         raise RequestException("bad url")
#     if "event_name" not in json:
#         raise RequestException("bad request")
#     if "package_id" not in json:
#         raise RequestException("bad request")
#     if "package_location" not in json:
#         raise RequestException("bad request")
#     if "package_metadata" not in json:
#         raise RequestException("bad request")
#     if "package_process_uuid" not in json:
#         raise RequestException("bad request")
#     mr = MockResponse()
#     mr.status_code = 200
#     return mr


class TngSdkValidationRestTest(unittest.TestCase):

    def setUp(self):
        # configure mocks
        # self.patcher = patch("requests.post", mock_requests_post)
        # self.patcher.start()
        # configure flask
        app.config['TESTING'] = True
        app.cliargs = None
        self.app = app.test_client()

    # def tearDown(self):
    #     self.patcher.stop()

    # def test_validations_v1_endpoint(self):
    #     # do a malformed post
    #     r = self.app.post("/api/v1/validations")
    #     self.assertEqual(r.status_code, 400)
    #     # do a post with a real validation for function
    #     # w/o errors
    #     r = self.app.post("/api/v1/packages",
    #                       content_type="multipart/form-data",
    #                       data={"package": (
    #                           open("misc/5gtango-ns-package-example.tgo",
    #                                "rb"), "5gtango-ns-package-example.tgo"),
    #                             "skip_store": True})
    #     self.assertEqual(r.status_code, 200)
    #     rd = json.loads(r.get_data(as_text=True))
    #     self.assertIn("package_process_uuid", rd)
        # do a post with a real validation for service
        # w/o errors

        # do a post with a real validation for fucntion
        # w/o errors

        # do a post with a real validation for service
        # with errors

    def test_rest_validation_function_syntax_ok(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'function=true&path=' + SAMPLES_DIR +
                          'samples/functions/' +
                          'valid-syntax-tng/default-vnfd-tng.yml&' +
                          'source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_function_syntax_ok_dext(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'function=true&path=' + SAMPLES_DIR +
                          'samples/functions/' +
                          'valid-syntax-tng/&dext=yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_function_syntax_ko(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'function=true&path=' + SAMPLES_DIR +
                          'samples/functions/' +
                          'invalid-syntax-tng/default-vnfd-tng.yml&' +
                          'source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 1)

    def test_rest_validation_service_syntax_ok(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'service=true&path=' + SAMPLES_DIR +
                          'samples/services/' +
                          'valid-son/valid.yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_service_syntax_ko(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'service=true&path=' + SAMPLES_DIR +
                          'samples/services/' +
                          'invalid-syntax-tng/unexpected_field.yml&' +
                          'source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 1)

    def test_rest_validation_function_integrity_ok(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/' +
                          'functions/valid-son/firewall-vnfd.yml&' +
                          'source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_function_integrity_ok_dext(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/functions/valid-son/&&dext=yml&' +
                          'source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_function_integrity_ko(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samplesfunctions/invalid_integrity-son/' +
                          'firewall-vnfd.yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 1)

    def test_rest_validation_function_integrity_ko_dext(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/functions/invalid_integrity-son/&' +
                          'dext=yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 3)

    def test_rest_validation_service_integrity_ok(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&service=true&path=' +
                          SAMPLES_DIR + 'samples/' +
                          'services/valid-son/valid.yml&dpath=' +
                          SAMPLES_DIR +
                          'samples/functions/valid-son/' +
                          '&dext=yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_service_integrity_ko(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&service=true&path=' +
                          SAMPLES_DIR + 'samples/' +
                          'services/valid-son/valid.yml&dpath=' +
                          SAMPLES_DIR +
                          'samples/functions/invalid_integrity-son/' +
                          '&dext=yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 3)

    def test_rest_validation_function_topology_ok(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/functions/valid-son/firewall-vnfd.yml' +
                          '&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_function_topology_ok_dext(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/functions/valid-son/&dext=yml' +
                          '&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_function_topology_ko(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/functions/invalid_topology-son/' +
                          'firewall-vnfd.yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 1)

    def test_rest_validation_function_topology_ko_dext(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&function=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/functions/invalid_topology-son/' +
                          '&dext=yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 1)

    def test_rest_validation_service_topology_ok(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&service=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/services/valid-son/valid.yml&dpath=' +
                          SAMPLES_DIR +
                          'samples/functions/valid-son/&dext=yml' +
                          '&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 0)

    def test_rest_validation_service_topology_ko(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&service=true' +
                          '&path=' + SAMPLES_DIR +
                          'samples/services/valid-son/valid.yml&dpath=' +
                          SAMPLES_DIR +
                          'samples/functions/invalid_topology-son/' +
                          '&dext=yml&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(d['error_count'], 1)

    def test_rest_validation_ko_many_arguments(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&service=true' +
                          '&function=true&&project=true&source=local&path=' +
                          SAMPLES_DIR + 'samples/' +
                          'functions/valid-son/firewall-vnfd.yml')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        expected_message = ('Not possible to validate function and service ' +
                            'and project in the same request')
        self.assertEqual(d['error_message'], expected_message)

    def test_rest_validation_ko_no_path(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true' +
                          '&function=true&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        expected_message = ('File path need it when local or ' +
                            'url source are used')
        self.assertEqual(d['error_message'], expected_message)

    def test_rest_validation_ko_no_descriptor(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&source=local')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        expected_message = ('Missing service, function and project ' +
                            'parameters')
        self.assertEqual(d['error_message'], expected_message)

    def test_rest_validation_ko_no_dpath_dext(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&source=local' +
                          '&service=true&path=' + SAMPLES_DIR +
                          'samples/services/valid-son/valid.yml')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        expected_message = ('Need functions path (dpath) and the extension ' +
                            'of it (dext) to validate service ' +
                            'integrity|topology|custom_rules')
        self.assertEqual(d['error_message'], expected_message)

    def test_rest_validation_ko_no_cfile(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'integrity=true&topology=true&' +
                          'source=local&custom=true' +
                          '&function=true&path=' + SAMPLES_DIR + 'samples/' +
                          'functions/valid-son/firewall-vnfd.yml')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        expected_message = ('Need rules file path (cfile) to validate ' +
                            'custom rules of descriptor')
        self.assertEqual(d['error_message'], expected_message)

    def test_rest_validation_ko_no_workspace(self):
        r = self.app.post('/api/v1/validations?sync=true&syntax=true&' +
                          'source=local&project=true&path=' +
                          SAMPLES_DIR + 'samples/' +
                          'projects/test_pv')
        data = r.data.decode('utf-8')
        d = ast.literal_eval(data)
        expected_message = ('Need workspace path (workspace) ' +
                            'to validate project')
        self.assertEqual(d['error_message'], expected_message)

    def test_rest_validation_ok_embedded_descriptor(self):
        url = ("/api/v1/validations?function=true&" +
               "source=embedded&sync=true&integrity=true&" +
               "syntax=true&topology=true")
        descriptor = open('/home/dani/Documents/firewall-vnfd.yml', 'rb')
        data = {
                'descriptor': (descriptor.name, descriptor, 'application/octet-stream'),
        }
        m = MultipartEncoder(data)
        headers = {'Content-Type': m.content_type}
        response = self.app.post(url, headers=headers, data=m)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)

    def test_rest_validation_ok_embedded_descriptor_rules(self):
        url = ("/api/v1/validations?function=true&" +
               "source=embedded&sync=true&integrity=true&" +
               "syntax=true&topology=true&custom=true")
        descriptor = open('/home/dani/Documents/firewall-vnfd.yml', 'rb')
        rules = open('/home/dani/Documents/custom_rule_1.yml', 'rb')
        data = {
                'descriptor': (descriptor.name, descriptor, 'application/octet-stream'),
                'rules': (rules.name, rules, 'application/octet-stream')
        }
        m = MultipartEncoder(data)
        headers = {'Content-Type': m.content_type}
        response = self.app.post(url, headers=headers, data=m)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
