[![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sdk-validation/master)](https://jenkins.sonata-nfv.eu/job/tng-sdk-validation/master)
[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-sdk-validation/wiki/images/sonata-5gtango-logo-500px.png" /></p>


# tng-sdk-validation

This repository contains the `tng-sdk-validation` component that is part of the European H2020 project [5GTANGO](http://www.5gtango.eu) NFV SDK. This component can be used to validate the syntax, integrity and topology of 5GTANGO file descriptors. Besides, `tng-sdk-validation` can be used through the CLI, as service  or as a micro-service running inside a docker container.

## Documentation

Please refer to the [wiki](https://github.com/sonata-nfv/tng-sdk-validation/wiki) of the project for a more detailed documentation.

# Installation and Dependencies

This tool has been designed to be executed in Linux system and Python 3.6 or higher. In addition, it is necessary to have installed the [tng-sdk-project](https://github.com/sonata-nfv/tng-sdk-project) before starting.

Other requirements are specified [here](https://github.com/sonata-nfv/tng-sdk-validation/blob/master/requirements.txt). They can be installed with the following statement:

```
pip3 install -r requirements.txt
```

## Automated:

It is possible to use the following command for automatic installation

```
pip3 install git+https://github.com/sonata-nfv/tng-sdk-validation.git
```

## Manual:
Manual installation is possible with:

```
git clone git@github.com:sonata-nfv/tng-sdk-validation.git
cd tng-sdk-validate
sudo python3 setup install
```

## Hint
It is a good practice to first create a new virtual environment in which all 5GTANGO SDK tools can be installed. You can do this as follows:

```
# get the path to your Python3 installation
which python3

# create a new virtualenv
virtualenv -p <path/to/python3> venv

# activate the virtualenv
source venv/bin/activate
```

# Usage

The validator can either be used as a command line tool (CLI mode) or as a micro service which offers a REST API.

## CLI mode

Runs the validator locally from the command line. Details about all possible parameters can be shown using:

```
tng-sdk-validate -h
```

### Validation

The CLI interface is designed for developer usage, allowing to quickly validate SDK descriptors:

* syntax only: `-s` or `--syntax`
* syntax and integrity `-i` or `--integrity`
* syntax, integrity and topology `-t` or `--topology`
* syntax, integrity, topology and custom rules `-c` or `--custom`

**Note**: If no validation level is chosen, the default level will be syntax, integrity and topology.

The tng-sdk-validation CLI tool can be used to validate one of the following components:

* `--project`

* `--service` - if integrity or superior validation is chosen, `--dpath` and `--dext` parameters must be specified.

* `--function`

* `--test`

* `--sla`

* `--slice`

* `--policy`
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

Runs the validator as a service that exposes a REST API.

### Run tng-skd-validate as a service

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

### Validation
Validator running as a service needs a **redis BSD** listening in port **6379** to perform the validation. Therefore:

```
#installation of redis server
apt-get install redis-server

#redis server listening in port 6379
redis-server --port 6379
```

And then, to run the validator:

```
# Run tng-sdk-validate service
tng-sdk-validate --api
```

### Some examples of validator calls through the API

```
# validation of descriptor in filesystem
curl -X POST 'http://localhost:5001/api/v1/validations?syntax=true&project=true&source=local&path=file_location_in_system'

#validation of descriptor using URL
curl -X POST 'http://localhost:5001/api/v1/validations?syntax=true&project=true&source=local&path=url_where_file_is_located'
```

If higher level of validation is required it is necessary to send all the levels in the query stream parameters, i.e.

```
syntax=true&integrity=true&topology=true
```
## Development
To contribute to the development of this 5GTANGO component, you may use the very same development workflow as for any other 5GTANGO Github project. That is, you have to fork the repository and create pull requests.

### Setup development environment

```
python3 setup.py
```

### CI Integration

All pull requests are automatically tested by Jenkins and will only be accepted if no test is broken.

### Run tests manually

You can also run the test manually on your local machine. To do so, you need to do:

```
pytest -v
```

## License

This 5GTANGO component is published under Apache 2.0 license. Please see the LICENSE file for more details.

#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Antón Román Portabales <anton.roman@quobis.com>
* Ana Pol González <ana.pol@quobis.com>
* Daniel Fernández Calvo <daniel.fernandez@quobis.es>
* Miguel Rivas Costa <miguel.rivas@quobis.es>

#### Feedback-Chanel

- You may use the mailing list [sonata-dev@lists.atosresearch.eu](mailto:sonata-dev@lists.atosresearch.eu)
* [GitHub issues](https://github.com/sonata-nfv/tng-sdk-validation/issues)
