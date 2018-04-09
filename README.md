# tng-sdk-validation
This repository contains the `tng-sdk-validation` component that is part of the European H2020 project [5GTANGO](http://www.5gtango.eu) NFV SDK. This component can be used to validate the syntax, integrity and topology of 5GTANGO SDK packages, projects, services and functions.
`tng-sdk-validation` can be used through the CLI or as a micro-service running inside a docker container.

> Work in progress. Please do not use this repository until this warning is removed.

## Installation

```bash
$ apt install python-pip
$ python setup.py install
```
## Usage
### CLI mode
The CLI interface is designed for developer usage, allowing to quickly validate SDK projects,package descriptors, service descriptors and function descriptors. The different levels of validation, namely syntax, integrity and topology can only be used in the following combinations:

- syntax only: `-s`
- syntax and integrity `-si`
- syntax, integrity and topology `-sit`
The tng-sdk-validation CLI tool can be used to validate one of the following components:
`-project` - to validate an SDK project, the `--workspace` parameter must be specified, otherwise the default location `$ HOME/.tng-workspace` is assumed. 
- package - to validate a package, only the `--package` should be specified indicating the path for the package file.
- service - in service validation, if the chosen level of validation comprises more than syntax (integrity or topology), the `--dpath` argument must be specified in order to indicate the location of the VNF descriptor files, referenced in the service. Has a standalone validation of a service, son-validate is not aware of a directory structure, unlike the project validation.
Moreover, the `--dext` parameter should also be specified to indicate the extension of descriptor files.
- function - this specifies the validation of an individual VNF. It is also possible to validate multiple functions in bulk contained inside a directory. To if the `--function` is a directory, it will search for descriptor files with the extension specified by parameter `--dext`.



```
user@hostname:~$ tng-sdk-validate -h
usage: tng-sdk-validate [-h] [-w WORKSPACE_PATH]
                        (--project PROJECT_PATH | --package PACKAGE_FILE | --service NSD | --function VNFD)
                        [--dpath DPATH] [--dext DEXT] [--syntax] [--integrity]
                        [--topology] [--debug]
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
  --function VNFD       Validate the specified function descriptor. If a
                        directory is specified, it will search for descriptor
                        files with extension defined in '--dext'
  --dpath DPATH         Specify a directory to search for descriptors.
                        Particularly useful when using the '--service'
                        argument.
  --dext DEXT           Specify the extension of descriptor files.
                        Particularly useful when using the '--function'
                        argument
  --syntax, -s          Perform a syntax validation.
  --integrity, -i       Perform an integrity validation.
  --topology, -t        Perform a network topology validation.
  --debug               Sets verbosity level to debug
Example usage:
        tng-sdk-validate --project /home/sonata/projects/project_X
                     --workspace /home/sonata/.son-workspace
        tng-sdk-validate --service ./nsd_file.yml --path ./vnfds/ --dext yml
        tng-sdk-validate --function ./vnfd_file.yml
        tng-sdk-validate --function ./vnfds/ --dext yml`
```


### Service mode
API overview
The tng-sdk-validation API provides the following functionalities:
- validate an SDK project, a package, a service or a function (`/validate/<object type> [POST]`)
- retrieve a list of available and validated objects (`/report [GET]`)
- retrieve the validation report for a specific object (`/report/result/<resource id> [GET]`)
- retrieve the validated network topology graph (`/report/topology/<resource id> [GET]`)
- retrieve the validated forwarding graphs structure (`/fwgraphs/<resource id>) [GET]`)

## Documentation

TODO (e.g. link to wiki page)

## Development

To contribute to the development of this 5GTANGO component, you may use the very same development workflow as for any other 5GTANGO Github project. That is, you have to fork the repository and create pull requests.

## License
The tng-sdk-validation is published under Apache 2.0 license. Please see the LICENSE file for more details.

#### Lead Developers
The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Antón Román Portabales
* Ana Pol González

#### Feedback-Chanel
* You may use the mailing list [tango-5g-wp4@lists.atosresearch.eu](mailto:tango-5g-wp4@lists.atosresearch.eu)
* [GitHub issues](https://github.com/sonata-nfv/tng-sdk-validation/issues)
