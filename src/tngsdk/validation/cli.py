#  Copyright (c) 2015 SONATA-NFV, 5GTANGO, UBIWHERE, QUOBIS SL.
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


LOG = logging.getLogger(os.path.basename(__file__))

def dispatch(self):
    if self._args.workspace:
        pass

    else:
        pass

def parse_args(input_args=None):
    parser = argparse.ArgumentParser(
        description="5GTANGO SDK validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example usage:
        tng-sdk-validate --project /home/sonata/projects/project_X
                     --workspace /home/sonata/.son-workspace
        tng-sdk-validate --service ./nsd_file.yml --path ./vnfds/ --dext yml
        tng-sdk-validate --function ./vnfd_file.yml
        tng-sdk-validate --function ./vnfds/ --dext yml
        """)

    exclusive_parser = parser.add_mutually_exclusive_group(
        required=True
    )

    parser.add_argument(
        "-w", "--workspace",
        help="Specify the directory of the SDK workspace for validating the SDK project.",
        # help="Specify the directory of the SDK workspace for validating the "
        #      "SDK project. If not specified will assume the directory: '{}'"
        #      .format(Workspace.DEFAULT_WORKSPACE_DIR),
        dest="workspace_path",
        required=False,
        default=None
    )

    exclusive_parser.add_argument(
        "--project",
        help="Validate the service of the specified SDK project.",
        # help="Validate the service of the specified SDK project. If "
        #      "not specified will assume the current directory: '{}'\n"
        #      .format(os.getcwd()),
        dest="project_path",
        required=False,
        default=None
    )
    exclusive_parser.add_argument(
        "--package",
        help="Validate the specified package descriptor.",
        dest="package_file",
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
        "--debug",
        help="Sets verbosity level to debug",
        dest="verbose",
        action="store_true",
        required=False,
        default=False
    )
    parser.add_argument(
        "--service-mode",
        help="Run validator in service mode with REST API.",
        dest="service-mode",
        action="store_true",
        required=False,
        default=False
    )

    if input_args is None:
        input_args = sys.argv[1:]

    return parser.parse_args(input_args)