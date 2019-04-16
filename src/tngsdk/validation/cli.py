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


LOG = logging.getLogger(os.path.basename(__file__))


def dispatch(args, validator):
    """
        'dispath' set in the 'validator' object the level of validation chosen by the user. By default, the validator
        makes topology level validation.
    """
    print("Printing all the arguments: {}\n".format(args))

    if args.vnfd:
        print("VNFD validation")
        validator.schema_validator.load_schemas("VNFD")
        if args.syntax:
            print("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False,
                                custom=False)
        elif args.integrity:
            print("Syntax and integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False,
                                custom=False)
        elif args.topology:
            print("Syntax, integrity and topology validation")
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=False)
        elif args.custom:
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=True, cfile=args.cfile)
            print("Syntax, integrity, topology  and custom rules validation")
        else:
            print("Default mode: Syntax, integrity and topology validation")
        if validator.validate_function(args.vnfd):
            if ((validator.error_count == 0) and (len(validator.customErrors) == 0)):
                print("No errors found in the VNFD")
            else:
                print("Errors in validation")
        return validator

    elif args.nsd:
        print("NSD validation")
        validator.schema_validator.load_schemas("NSD")
        if args.syntax:
            print("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False)
        elif args.integrity:
            print("Syntax and integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False,
                                dpath=args.dpath)
        elif args.topology:
            print("Syntax, integrity and topology validation")
            validator.configure(syntax=True, integrity=True, topology=True,
                                dpath=args.dpath)
        elif args.custom:
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=True, cfile=args.cfile,
                                dpath=args.dpath)
            print("Syntax, integrity, topology  and custom rules validation")
        else:
            validator.configure(syntax=True, integrity=True, topology=True,
                                dpath=args.dpath)
            print("Default mode: Syntax, integrity and topology validation")

        if validator.validate_service(args.nsd):
            if ((validator.error_count == 0) and (len(validator.customErrors) == 0)):
                    print("No errors found in the Service descriptor validation")
            else:
                    print("Errors in custom rules validation")
        return validator

    elif args.project_path:
        print("Project descriptor validation")
        validator.schema_validator.load_schemas("NSD")
        if args.syntax:
            print("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False,
                                workspace_path=args.workspace_path)
        elif args.integrity:
            print("Syntax and integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False,
                                workspace_path=args.workspace_path)
        elif args.topology:
            print("Syntax, integrity and topology validation")
            validator.configure(syntax=True, integrity=True, topology=True,
                                workspace_path=args.workspace_path)

        elif args.custom:
            validator.configure(syntax=True, integrity=True, topology=True,
                                custom=True, cfile=args.cfile)
            print("Syntax, integrity, topology  and custom rules validation")
        else:
            print("Default mode: Syntax, integrity and topology validation")

        if validator.validate_project(args.project_path):
            print('Cant validate the project descriptors')
        else:
            if validator.error_count == 0:
                if len(validator.customErrors) == 0:
                    print("No errors found in the validation of the project descriptors")
                else:
                    print("Errors in custom rules validation")
        return validator
    elif args.tstd:
        print("Test descriptor validation")
        if args.syntax:
            print("Syntax validation")
            validator.configure(syntax=True, integrity=False, topology=False, custom=False)
        elif args.integrity:
            print("Integrity validation")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)
        else:
            print("Default test descriptor validation syntax and integrity")
            validator.configure(syntax=True, integrity=True, topology=False, custom=False)

    if not validator.validate_test(args.tstd):
        print('Cant validate the test descriptors')
    else:
        if validator.error_count == 0:
            if len(validator.customErrors) == 0:
                print("No errors found in the validation of the test descriptors")
            else:
                print("Errors in validation")
    return validator
def check_args(args):
    # TODO: the validator accepts two level parameter in the input parametes i.e. -i -s. It does not have sense
    if args.project_path:
        if not(args.custom):
            return True
        else:
            if not(args.cfile):
                print('Invalid parameters. To validate custom_rules of a project descriptors'
                '--cfile must be specified')
            return False
    elif (args.nsd):
        if args.syntax:
            return True
        elif (args.integrity or args.topology or args.custom) and (not(args.dext) and not(args.dpath)):
            print("Invalid parameters. To validate the "
                  "integrity, topology or custom rules of a service descriptors"
                  "both' --dpath' and '--dext' parameters must be "
                  "specified.")
            return False
        elif not(args.syntax) and not(args.integrity) and not(args.topology) and not(args.dpath):
            print("Invalid parameters. To validate the "
                  "integrity, topology or custom rules of a service descriptors"
                  "both' --dpath' and '--dext' parameters must be "
                  "specified.")
            return False
        elif args.custom and not(args.cfile):
            print("Invalid parameters. To validate the "
                  "custom rules of a service descriptors"
                  "both' --dpath' and '--dext' parameters must be "
                  "specified (to validate the topology/integrity) and "
                  "'--cfile' must be specified")
            return False
        else:
            return True
    elif args.vnfd:
        if args.custom and not(args.cfile):
                print("Invalid parameters. To validate the "
                      "custom rules of a service descriptors"
                      "'--cfile' must be specified")
                return False
        else:
            return True
    elif args.tstd:
        # TODO: Does the test descriptor have to bear some type of custom rules?
        if args.topology or args.custom:
            print("Invalid parameters. The validation level "
                  "of the test descriptor is syntax or integrity")
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

    - Validation of service descriptors.
        tng-sdk-validate  --service path/to/example_nsd.yml --dpath path/to/function_folder --dext yml

    - Validation of all function (VNF/CNF) descriptors in a folder.
        tng-sdk-validate --function path/to/function_folder/
        tng-sdk-validate --function path/to/function_folder/ --dext yml

    - Validation of individual function (VNF/CNF) descriptor.
        tng-sdk-validate --function path/to/example_function.yml
        tng-sdk-validate --function path/to/example_function.yml --dext yml

    - Validation of individual test (TSTD) descriptor.
        tng-sdk-validate --test path/to/example_test.yml
        tng-sdk-validate --test path/to/example_test.yml --dext yml
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
    """
    exclusive_parser.add_argument
        "--package",
        help="Validate the specified package descriptor.",
        dest="package_file",
        required=False,
        default=None
    )
    """
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
    print("CLI input arguments: {}".format(input_args))
    return parser.parse_args(input_args)
