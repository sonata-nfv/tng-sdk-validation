[![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sdk-validation/master)](https://jenkins.sonata-nfv.eu/job/tng-sdk-validation/master)
[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-sdk-validation/wiki/images/sonata-5gtango-logo-500px.png" /></p>


# tng-sdk-validation


This repository contains the `tng-sdk-validation` component that is part of the European H2020 project [5GTANGO](http://www.5gtango.eu) NFV SDK. This component can be used to validate the syntax, integrity and topology of 5GTANGO SDK packages, projects, services and functions. This validation tool helps to make sure that the descriptors of different services and functions are valid and will create working service. There is an additional feature to include custom rules in YAML files to validate the descriptors but it is still under development and not available in master.

`tng-sdk-validation` can be used through the CLI, as service  or as a micro-service running inside a docker container.

## Dependencies

* This tool has been designed to be executed in Linux system and Python 3.6 or higher.

* It is necessary to install [tng-sdk-project](https://github.com/sonata-nfv/tng-sdk-project) first as *tng-sdk-validation* depends on it. Please follow the instructions provided in the Readme file to install it.


## Installation

It is possible use the following command for automatic installation
```
pip3 install git+https://github.com/sonata-nfv/tng-sdk-validation.git
```
Alternatively:
1. Clone the master branch of this repository and access the directory.

2. Then install the Python dependencies defined in requierements file.
```bash
$ pip3 install -r requirements.txt
```
3. The last step is to install *tng-sdk-validation* tool.
```bash
$ python3 setup.py install
```
4. Once installed, the command `tng-sdk-validate` should be available in your Linux system.

## Usage

### CLI mode

The CLI interface is designed for developer usage, allowing to quickly validate SDK projects descriptors, package descriptors, service descriptors and function descriptors. The different levels of validation are syntax, integrity, topology and custom_rules. They can only be used in the following combinations:

* syntax only: `-s` or `--syntax`
* syntax and integrity `-i` or `--integrity`
* syntax, integrity and topology `-t` or `--topology`
* syntax, integrity, topology and custom_rules `-c` or `--custom`

The tng-sdk-validation CLI tool can be used to validate one of the following components:

* `--project` - If this option is chosen, all descriptors in the project will be validated. It is possible to use `--workspace`/`-w` parameter to set a particular workspace path, otherwise, the path is `$ HOME/.tng-workspace`.

* `--service` - It is possible validate only the syntax of the service descriptor in the case of use `--syntax`. If a superior validation is chosen (for instance integrity), it is necessary to specify `--dpath` and `--dext` parameters. Using the superior validation the functions referenced by the descriptor will be validated too.

* `--function` - There are two modes of function descriptor validation, validate an individual function descriptor or validation of all descriptors inside a directory.

```
quobis@quobis-UX303UA:~/tng-sdk-validation$ tng-sdk-validate -h
CLI input arguments: ['-h']
usage: tng-validate [-h] [-w WORKSPACE_PATH]
                    (--project PROJECT_PATH | --package PACKAGE_FILE | --service NSD | --function VNFD | --api)
                    [--dpath DPATH] [--dext DEXT] [--syntax] [--integrity]
                    [--topology] [--custom] [--cfile CFILE] [--debug]
                    [--mode {stateless,local}] [--host SERVICE_ADDRESS]
                    [--port SERVICE_PORT]

5GTANGO SDK validator

optional arguments:
  -h, --help            show this help message and exit
  -w WORKSPACE_PATH, --workspace WORKSPACE_PATH
                        Specify the directory of the SDK workspace for
                        validating the SDK project.
  --project PROJECT_PATH
                        Validate the service of the specified SDK project.
  --package PACKAGE_FILE
                        Validate the specified package descriptor.
  --service NSD         Validate the specified service descriptor. The
                        directory of descriptors referenced in the service
                        descriptor should be specified using the argument '--
                        path'.
  --function VNFD/CNFD  Validate the specified function descriptor. If a
                        directory is specified, it will search for descriptor
                        files with extension defined in '--dext'
  --api                 Run validator in service mode with REST API.
  --dpath DPATH         Specify a directory to search for descriptors.
                        Particularly useful when using the '--service'
                        argument.
  --dext DEXT           Specify the extension of descriptor files.
                        Particularly useful when using the '--function'
                        argument
  --syntax, -s          Perform a syntax validation.
  --integrity, -i       Perform an integrity validation.
  --topology, -t        Perform a network topology validation.
  --custom, -c          Perform a network custom rules validation.
  --cfile CFILE         Specify the file with the custom rules to validate
  --debug               Sets verbosity level to debug
  --mode {stateless,local}
                        Specify the mode of operation. 'stateless' mode will
                        run as a stateless service only. 'local' mode will run
                        as a service and will also provide automatic
                        monitoring and validation of local SDK projects,
                        services, etc. that are configured in the developer
                        workspace
  --host SERVICE_ADDRESS
                        Bind address for this service
  --port SERVICE_PORT   Bind port number

Example usage:

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

```

## Documentation

Please refer to the [wiki](https://github.com/sonata-nfv/tng-sdk-validation/wiki) of the project for a more detailed documentation.

## License

The tng-sdk-validation is published under Apache 2.0 license. Please see the LICENSE file for more details.

#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Antón Román Portabales <anton.roman@quobis.com>
* Ana Pol González <ana.pol@quobis.com>
* Daniel Fernández Calvo <daniel.fernandez@quobis.es>

#### Feedback-Chanel

* You may use the mailing list [tango-5g-wp4@lists.atosresearch.eu](mailto:tango-5g-wp4@lists.atosresearch.eu)
* [GitHub issues](https://github.com/sonata-nfv/tng-sdk-validation/issues)
