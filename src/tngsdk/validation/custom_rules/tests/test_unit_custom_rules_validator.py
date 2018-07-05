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
import tempfile
import shutil
from tngsdk.validation.custom_rules import validator_custom_rules

SAMPLE_DIR = 'src/tngsdk/validation/custom_rules/tests/samples/'


class TngSdkValidationCustomRulesTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_custom_rules_process_rules_ok(self):
        rules = SAMPLE_DIR + 'custom_rule_1.yml'
        descriptor = SAMPLE_DIR + 'function_1_ok.yml'
        val = (validator_custom_rules.process_rules(rules, descriptor))
        self.assertFalse(val)

    def test_custom_rules_process_rules_ko(self):
        rules = SAMPLE_DIR + 'custom_rule_1.yml'
        descriptor = SAMPLE_DIR + 'function_1_ko.yml'
        val = (validator_custom_rules.process_rules(rules, descriptor))
        self.assertTrue(val)


if __name__ == "__main__":
    unittest.main()
