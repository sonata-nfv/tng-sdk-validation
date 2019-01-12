#  Copyright (c) 2015 SONATA-NFV, 5GTANGO, UBIWHERE, QUOBIS SL.
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
# Neither the name of the SONATA-NFV, 5GTANGO, UBIWHERE, QUOBIS SL.
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
import coloredlogs
import os

from tngsdk.validation import cli, rest
from tngsdk.validation.validator import Validator

LOG = logging.getLogger(os.path.basename(__file__))


def logging_setup():
    os.environ["COLOREDLOGS_LOG_FORMAT"] \
    = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"


def main():
    logging_setup()
    args = cli.parse_args()
    # TODO better log configuration (e.g. file-based logging)
    if args.verbose:
        coloredlogs.install(level="DEBUG")
    else:
        coloredlogs.install(level="INFO")

    # TODO validate if args combination makes any sense
    if cli.check_args(args):
        if args.api:
            # TODO start validator in service mode
            print("Validator started as an API in IP: {} and port {}"
                  .format(args.service_address, args.service_port))
            rest.serve_forever(args)
            pass
        else:
            # run validator in CLI mode
            validator = Validator()
            result_validator = cli.dispatch(args, validator)
            if result_validator.error_count > 0:
                exit(1)  # exit with error code
            exit(0)
    else:
        print('Invalid arguments. Please check the help (-h)')
