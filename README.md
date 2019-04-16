[![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sdk-validation/master)](https://jenkins.sonata-nfv.eu/job/tng-sdk-validation/master)
[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-sdk-validation/wiki/images/sonata-5gtango-logo-500px.png" /></p>


# tng-sdk-validation


This repository contains the `tng-sdk-validation` component that is part of the European H2020 project [5GTANGO](http://www.5gtango.eu) NFV SDK. This component can be used to validate the syntax, integrity and topology of 5GTANGO SDK packages, projects, services and functions. This validation tool helps to make sure that the descriptors of different services and functions are valid and will create working service. There is an additional feature to include custom rules in YAML files to validate the descriptors but it is still under development and not available in master.

`tng-sdk-validation` can be used through the CLI, as service  or as a micro-service running inside a docker container.

# Installation and Dependencies

This tool has been designed to be executed in Linux system and Python 3.6 or higher. It's necessary to install [tng-sdk-project](https://github.com/sonata-nfv/tng-sdk-project) first because first as *tng-sdk-validation* depends on it. Moreover, other requirements of the tool are [requirements](https://github.com/MiguelRivasQuobis/tng-sdk-validation/blob/master/requirements.txt).
You can install it with the following statement.
```
pip3 install git -r requirements.txt
```

## Automated:

It is possible use the following command for automatic installation
```
pip3 install git+https://github.com/sonata-nfv/tng-sdk-validation.git
```
## Manual:

```
git clone git@github.com:sonata-nfv/tng-sdk-validate.git
cd tng-sdk-validate
sudo python3 setup install
```

# Usage

The packager can either be used as command line tool (CLI mode) or deployed as a micro service which offers a REST API

## CLI mode

Runs the validator locally from the command line. Details about all possible parameters can be shown using:

```
tng-sdk-validate -h
```
### Validation

The CLI interface is designed for developer usage, allowing to quickly validate SDK projects descriptors, package descriptors, service descriptors and function descriptors. The different levels of validation are syntax, integrity, topology and custom_rules. They can only be used in the following combinations:

* syntax only: `-s` or `--syntax`
* syntax and integrity `-i` or `--integrity`
* syntax, integrity and topology `-t` or `--topology`
* syntax, integrity, topology and custom_rules `-c` or `--custom`
* If no validation level is chosen, the default level will be syntax, integrity and topology

The tng-sdk-validation CLI tool can be used to validate one of the following components:

* `--project` - If this option is chosen, all descriptors in the project will be validated. It is possible to use `--workspace`/`-w` parameter to set a particular workspace path, otherwise, the path is `$ HOME/.tng-workspace`.

* `--service` - It is possible validate only the syntax of the service descriptor in the case of use `--syntax`. If a superior validation is chosen (for instance integrity), it is necessary to specify `--dpath` and `--dext` parameters. Using the superior validation the functions and/ or tests descriptors referenced by the descriptor will be validated too.

* `--function` - There are two modes of function descriptor validation, validate an individual function descriptor or validation of all descriptors inside a directory.

* `--test` - It is possible to validate a individual test descriptor or all the test descriptors inside a directory. (Is not possible to validate topology in tests descriptors)

### Some examples of validator calls:
```
#project descriptors syntax validation with default workspace
tng-sdk-validate -s --project path/to/project/

#service descriptor integrity validation
tng-sdk-validate -i --service path/to/example_nsd.yml --dpath path/to/function_folder --dext yml

#function descriptors topology validation
tng-sdk-validate -t --function path/to/function_folder/ --dext yml

#test descriptor default validation
tng-sdk-validate --test path/to/example_function.yml
```

## Service mode

Runs the packager as a service that exposes a REST API

### Run tng-skd-validate as a serviceif any fruit

#### Bare metal
```
tng-skd-validate --api
```
#### Docker-based
```
#create the docker image
docker build --no-cache -f ./Dockerfile -t registry.sonata-nfv.eu:5000/tng-sdk-validation .

#run the image
docker run --rm -d --name tng-sdk-validate registry.sonata-nfv.eu:5000/tng-sdk-validation
```
#### Validation


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
