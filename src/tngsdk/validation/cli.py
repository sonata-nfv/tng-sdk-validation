#  Copyright (c) 2018 SONATA-NFV, 5GTANGO, UBIWHERE, QUOBIS SL.
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
import argparse
import os
import sys

from tngsdk.validation.validator import Validator
from tngsdk.project.project import Project
from tngsdk.validation.logger import TangoLogger


LOG = TangoLogger.getLogger(__name__)


def dispatch(args, validator):
    """
        'dispath' set in the 'validator' object the level of validation
        chosen by the user. By default, the validator
        makes topology level validation.
    """
    LOG.info("Printing all the arguments: {}\n".format(args))
    if args.vnfd:
        LOG.info("VNFD validation")
        validator.schema_validator.load_schemas("VNFD")
        if args.syntax:
            LOG.info("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False,
                                custom=False)
        elif args.integrity:
            LOG.info("Syntax and integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False,
                                custom=False)
        elif args.topology:
            LOG.info("Syntax, integrity and topology validation")
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=False)
        elif args.custom:
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=True, cfile=args.cfile)
            LOG.info("Syntax, integrity, topology  and custom rules validation")
        else:
            LOG.info("Default mode: Syntax, integrity and topology validation")
        if validator.validate_function(args.vnfd):
            if ((validator.error_count == 0) and
            (len(validator.customErrors) == 0)):
                LOG.info("No errors found in the VNFD")
            else:
                LOG.info("Errors in validation")
        return validator

    elif args.nsd:
        LOG.info("NSD validation")
        validator.schema_validator.load_schemas("NSD")
        if args.syntax:
            LOG.info("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False)
        elif args.integrity:
            LOG.info("Syntax and integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False,
                                dpath=args.dpath)
        elif args.topology:
            LOG.info("Syntax, integrity and topology validation")
            validator.configure(syntax=True, integrity=True, topology=True,
                                dpath=args.dpath)
        elif args.custom:
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=True, cfile=args.cfile,
                                dpath=args.dpath)
            LOG.info("Syntax, integrity, topology  and custom rules validation")
        else:
            validator.configure(syntax=True, integrity=True, topology=True,
                                dpath=args.dpath)
            LOG.info("Default mode: Syntax, integrity and topology validation")

        if validator.validate_service(args.nsd):
            if ((validator.error_count == 0) and (len(validator.customErrors) == 0)):
                    LOG.info("No errors found in the Service descriptor validation")
            else:
                    LOG.info("Errors in custom rules validation")
        return validator

    elif args.project_path:
        LOG.info("Project descriptor validation")
        validator.schema_validator.load_schemas("NSD")
        if args.syntax:
            LOG.info("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False,
                                workspace_path=args.workspace_path)
        elif args.integrity:
            LOG.info("Syntax and integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False,
                                workspace_path=args.workspace_path)
        elif args.topology:
            LOG.info("Syntax, integrity and topology validation")
            validator.configure(syntax=True, integrity=True, topology=True,
                                workspace_path=args.workspace_path)

        elif args.custom:
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=True, cfile=args.cfile)
            LOG.info("Syntax, integrity, topology  and custom rules validation")
        else:
            LOG.info("Default mode: Syntax, integrity and topology validation")

        if not validator.validate_project(args.project_path):
            LOG.info('Cant validate the project descriptors')
        else:
            if validator.error_count == 0:
                if len(validator.customErrors) == 0:
                    LOG.info("No errors found in the validation of the project descriptors")
                else:
                    LOG.info("Errors in custom rules validation")
        return validator
    elif args.tstd:
        LOG.info("Test descriptor validation")
        if args.syntax:
            LOG.info("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False, custom=False)
        elif args.integrity:
            LOG.info("Integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)
        else:
            LOG.info("Default test descriptor validation syntax and integrity")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)

        if not validator.validate_test(args.tstd):
            LOG.info('Cant validate the test descriptors')
        else:
            if validator.error_count == 0 and len(validator.customErrors) == 0:
                LOG.info("No errors found in the validation of the test descriptors")
            else:
                LOG.info("Errors in validation")
        return validator
    elif args.nstd:
        LOG.info("Slice descriptor validation")
        validator.schema_validator.load_schemas("NSTD")

        if args.syntax:
            LOG.info("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False, custom=False)
        elif args.integrity:
            LOG.info("Integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)
        else:
            LOG.info("Default test descriptor validation syntax and integrity")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)

        if not validator.validate_slice(args.nstd):
            LOG.info('Cant validate the slice descriptors')
        else:
            if validator.error_count == 0 and len(validator.customErrors) == 0:
                LOG.info("No errors found in the validation of the slice descriptors")
            else:
                LOG.info("Errors in validation")
        return validator
    elif args.slad:
        LOG.info("SLA descriptor validation")
        validator.schema_validator.load_schemas("SLAD")
        if args.syntax:
            LOG.info("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False, custom=False)
        elif args.integrity:
            LOG.info("Integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)
        else:
            LOG.info("Default test descriptor validation syntax and integrity")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)

        if not validator.validate_sla(args.slad):
            LOG.info('Cant validate the sla descriptors')
        else:
            if validator.error_count == 0 and len(validator.customErrors) == 0:
                LOG.info("No errors found in the validation of the sla descriptors")
            else:
                LOG.info("Errors in validation")
        return validator
    elif args.rpd:
        LOG.info("RP descriptor validation")
        validator.schema_validator.load_schemas("RPD")
        if args.syntax:
            LOG.info("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False, custom=False)
        elif args.integrity:
            LOG.info("Integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)
        else:
            LOG.info("Default test descriptor validation syntax and integrity")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)

        if not validator.validate_runtime_policy(args.rpd):
            LOG.info('Cant validate the sla descriptors')
        else:
            if validator.error_count == 0 and len(validator.customErrors) == 0:
                LOG.info("No errors found in the validation of the sla descriptors")
            else:
                LOG.info("Errors in validation")
        return validator
def check_args(args):
    if args.project_path:
        if not(args.custom):
            return True
        else:
            if not(args.cfile):
                LOG.info('Invalid parameters. To validate custom_rules of a project descriptors'
                '--cfile must be specified')
            return False
    elif (args.nsd):
        if args.syntax:
            return True
        elif (args.integrity or args.topology or args.custom) and (not(args.dext) and not(args.dpath)):
            LOG.info("Invalid parameters. To validate the "
                  "integrity, topology or custom rules of a service descriptors"
                  "both' --dpath' and '--dext' parameters must be "
                  "specified.")
            return False
        elif not(args.syntax) and not(args.integrity) and not(args.topology) and not(args.dpath):
            LOG.info("Invalid parameters. To validate the "
                  "integrity, topology or custom rules of a service descriptors"
                  "both' --dpath' and '--dext' parameters must be "
                  "specified.")
            return False
        elif args.custom and not(args.cfile):
            LOG.info("Invalid parameters. To validate the "
                  "custom rules of a service descriptors"
                  "both' --dpath' and '--dext' parameters must be "
                  "specified (to validate the topology/integrity) and "
                  "'--cfile' must be specified")
            return False
        else:
            return True
    elif args.vnfd:
        if args.custom and not(args.cfile):
                LOG.info("Invalid parameters. To validate the "
                      "custom rules of a service descriptors"
                      "'--cfile' must be specified")
                return False
        else:
            return True
    elif args.tstd:
        # TODO have custom rules sense here?
        if args.topology or args.custom:
            LOG.info("Invalid parameters. The validation level "
                  "of the test descriptor is syntax or integrity")
        else:
            return True

    elif args.nstd:
        # TODO have custom rules sense here?
        if args.topology or args.custom:
            LOG.info("Invalid parameters. The validation level "
                  "of the slice descriptor is syntax or integrity")
        else:
            return True
    elif args.slad:
        # TODO have custom rules sense here?
        if args.topology or args.custom:
            LOG.info("Invalid parameters. The validation level "
                  "of the sla descriptor is syntax or integrity")
        else:
            return True
    elif args.rpd:
        # TODO have custom rules sense here?
        if args.topology or args.custom:
            LOG.info("Invalid parameters. The validation level "
                  "of the sla descriptor is syntax or integrity")
        else:
            return True
    else:
        return True

def parse_args(input_args=None):
    #TODO Examples for custom rules.
    parser = argparse.ArgumentParser(
        description="5GTANGO SDK validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example usage:

    - Validation of project descriptors in a particular workspace.
        tng-sdk-validate --project path/to/project/ --workspace path/to/workspace

    - Validation of project descriptors in the default workspace ($ HOME/.tng-workspace).
        tng-sdk-validate --project path/to/project/

    - Validation of service (NSD) descriptors.
        tng-sdk-validate  --service path/to/example_nsd.yml --dpath path/to/function_folder --dext yml

    - Validation of all function (VNFD/CNFD) descriptors in a folder.
        tng-sdk-validate --function path/to/function_folder/
        tng-sdk-validate --function path/to/function_folder/ --dext yml

    - Validation of individual function (VNFD/CNFD) descriptor.
        tng-sdk-validate --function path/to/example_function.yml
        tng-sdk-validate --function path/to/example_function.yml --dext yml

    - Validation of individual test (TSTD) descriptor.
        tng-sdk-validate --test path/to/example_test.yml
        tng-sdk-validate --test path/to/example_test.yml --dext yml

    - Validation of individual network slice template (NSTD) descriptor.
        tng-sdk-validate --slice path/to/example_slice.yml
        tng-sdk-validate --slice path/to/example_slice.yml --dext yml

    - Validation of individual sla (SLAD) descriptor.
        tng-sdk-validate --sla path/to/example_sla.yml
        tng-sdk-validate --sla path/to/example_sla.yml --dext yml

    - Validation of individual runtime policy (RPD) descriptor.
        tng-sdk-validate --policy path/to/example_policy.yml
        tng-sdk-validate --policy path/to/example_policy.yml --dext yml
    """)

    exclusive_parser = parser.add_mutually_exclusive_group(
        required=True
    )

    parser.add_argument(
        "-w", "--workspace",
        help="Specify the directory of the SDK workspace for " +
             "validating the descriptors of SDK project.",
        # help="Specify the directory of the SDK workspace for validating the "
        #      "SDK project. If not specified will assume the directory: '{}'"
        #      .format(Workspace.DEFAULT_WORKSPACE_DIR),
        dest="workspace_path",
        required=False,
        default=None
    )
    parser.add_argument(
        "--loglevel",
        help="Directly specify loglevel. Default: INFO",
        required=False,
        default=None,
        dest="log_level")
    parser.add_argument(
        "--logjson",
        help="Use 5GTANGO JSON-based logging. Default: False",
        required=False,
        default=False,
        dest="logjson",
        action="store_true")

    exclusive_parser.add_argument(
        "--project",
        help="Validate the service descriptors of the specified SDK project.",
        # help="Validate the service of the specified SDK project. If "
        #      "not specified will assume the current directory: '{}'\n"
        #      .format(os.getcwd()),
        dest="project_path",
        required=False,
        default=None
    )

    exclusive_parser.add_argument(
        "--slice",
        help="Validate the specified netwok slice template descriptor.",
        dest="nstd",
        required=False,
        default=None
    )
    exclusive_parser.add_argument(
        "--policy",
        help="Validate the specified runtime policy descriptor.",
        dest="rpd",
        required=False,
        default=None
    )

    exclusive_parser.add_argument(
        "--sla",
        help="Validate the specified SLA descriptor.",
        dest="slad",
        required=False,
        default=None
    )
    exclusive_parser.add_argument(
        "--service",
        help="Validate the specified service descriptor. "
             "The directory of descriptors referenced in the service "
             "descriptor should be specified using the argument '--path'.",
        dest="nsd",
        required=False,
        default=None
    )
    exclusive_parser.add_argument(
        "--function",
        help="Validate the specified function descriptor. If a directory is "
             "specified, it will search for descriptor files with extension "
             "defined in '--dext'",
        dest="vnfd",
        required=False,
        default=None
    )
    exclusive_parser.add_argument(
        "--test",
        help="validate the specified test descriptor",
        dest="tstd",
        required=False,
        default=None
    )
    exclusive_parser.add_argument(
        "--api",
        help="Run validator in service mode with REST API.",
        dest="api",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "--dpath",
        help="Specify a directory to search for descriptors. Particularly "
             "useful when using the '--service' argument.",
        required=False,
        default=None
    )
    parser.add_argument(
        "--dext",
        help="Specify the extension of descriptor files. Particularly "
             "useful when using the '--function' argument",
        required=False,
        default=None
    )
    parser.add_argument(
        "--syntax", "-s",
        help="Perform a syntax validation.",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "--integrity", "-i",
        help="Perform an integrity validation.",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "--topology", "-t",
        help="Perform a network topology validation.",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "--custom", "-c",
        help="Perform a network custom rules validation.",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "--cfile",
        help="Specify the file with the custom rules to validate",
        dest="cfile",
        required=False,
        default=None
    )
    parser.add_argument(
        "--debug",
        help="Sets verbosity level to debug",
        dest="verbose",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "--mode",
        choices=['stateless', 'local'],
        default='stateless',
        help="Specify the mode of operation. 'stateless' mode will run as "
             "a stateless service only. 'local' mode will run as a "
             "service and will also provide automatic monitoring and "
             "validation of local SDK projects, services, etc. that are "
             "configured in the developer workspace",
        required=False
    )
    parser.add_argument(
        "--host",
        help="Bind address for this service",
        default='127.0.0.1',
        required=False,
        dest="service_address"
    )
    parser.add_argument(
        "--port",
        default=5001,
        type=int,
        help="Bind port number",
        required=False,
        dest="service_port"
    )
    if input_args is None:
        input_args = sys.argv[1:]
    LOG.info("CLI input arguments: {}".format(input_args))
    return parser.parse_args(input_args)
