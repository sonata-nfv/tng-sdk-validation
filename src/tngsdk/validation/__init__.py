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
from tngsdk.validation.logger import TangoLogger

LOG = TangoLogger.getLogger(os.path.basename(__file__))

def setup_logging(args):
    """
    Configure logging.
    """
    log_level = logging.INFO
    # get loglevel from environment or --loglevel
    log_level_str = os.environ.get("LOGLEVEL", "INFO")
    if args.log_level:  # overwrite if present
        log_level_str = args.log_level
    # parse
    log_level_str = str(log_level_str).lower()
    if log_level_str == "debug":
        log_level = logging.DEBUG
    elif log_level_str == "info":
        log_level = logging.INFO
    elif log_level_str == "warning":
        log_level = logging.WARNING
    elif log_level_str == "error":
        log_level = logging.ERROR
    else:
        LOG.info("Loglevel '{}' unknown.".format(log_level_str))
    # if "-v" is there set to debug
    if args.verbose:
        log_level = logging.DEBUG
    # select logging mode
    log_json = os.environ.get("LOGJSON", args.logjson)
    # configure all TangoLoggers
    TangoLogger.reconfigure_all_tango_loggers(
        log_level=log_level, log_json=log_json)


def main():
    args = cli.parse_args()
    setup_logging(args)
    # TODO better log configuration (e.g. file-based logging)
    if args.verbose:
        coloredlogs.install(level="DEBUG")
    else:
        coloredlogs.install(level="INFO")

    # TODO validate if args combination makes any sense
    if cli.check_args(args):
        if args.api:
            # TODO start validator in service mode
            LOG.info("Validator started as an API in IP: {} and port {}"
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
        LOG.info('Invalid arguments. Please check the help (-h)')
