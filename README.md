[![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sdk-validation/master)](https://jenkins.sonata-nfv.eu/job/tng-sdk-validation/master)
[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)

<p align="center"><img src="https://github.com/sonata-nfv/tng-sdk-validation/wiki/images/sonata-5gtango-logo-500px.png" /></p>


# Validation tool

This repository contains the `tng-sdk-validation` component that is part of the European H2020 project [5GTANGO](http://www.5gtango.eu) NFV SDK. This component can be used to validate the syntax, integrity and topology of 5GTANGO file descriptors. Besides, `tng-sdk-validation` can be used through the CLI, as service  or as a micro-service running inside a docker container.

# Dependencies

This tool has been designed to be executed in Linux system and Python 3.6 or higher. In addition, it is necessary to have installed the [tng-sdk-project](https://github.com/sonata-nfv/tng-sdk-project) before starting.

Other requirements are specified [here](https://github.com/sonata-nfv/tng-sdk-validation/blob/master/requirements.txt). They can be installed with the following statement:

```
pip3 install -r requirements.txt
```

# Installation
## Automated

It is possible to use the following command for automatic installation

```
pip3 install git+https://github.com/sonata-nfv/tng-sdk-validation.git
```

## Manual
Manual installation is possible with:

```
git clone git@github.com:sonata-nfv/tng-sdk-validation.git
cd tng-sdk-validation
sudo python3 setup.py install
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

More details on the usage and some examples of the validator can be found on the [wiki](https://github.com/sonata-nfv/tng-sdk-validation/wiki).

## Service mode

Runs the validator as a service that exposes a REST API:

```
tng-sdk-validate --api
```

### Running dependencies
Validator running as a service needs a **redis BSD** listening in port **6379** to perform the validation. Therefore:

```
#installation of redis server
apt-get install redis-server

#redis server listening in port 6379
redis-server --port 6379
```

## Docker-based service

```
#create the docker image
docker build --no-cache -f ./Dockerfile -t registry.sonata-nfv.eu:5000/tng-sdk-validation .

#run the image
docker run --rm -d --name tng-sdk-validate registry.sonata-nfv.eu:5000/tng-sdk-validation
```

# Development

To contribute to the development of this 5GTANGO component, you may use the very same development workflow as for any other 5GTANGO Github project. That is, you have to fork the repository and create pull requests.

## Setup development environment

```
python3 setup.py
```

# Tests
Validator tests can be run manually on your local machine. To do so, you need to do:

```
pytest -v
```

# Documentation

Please refer to the [wiki](https://github.com/sonata-nfv/tng-sdk-validation/wiki) of the project for a more detailed documentation.

# License

This 5GTANGO component is published under Apache 2.0 license. Please see the LICENSE file for more details.

## Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Antón Román Portabales <anton.roman@quobis.com>
* Ana Pol González <ana.pol@quobis.com>
* Daniel Fernández Calvo <daniel.fernandez@quobis.es>
* Miguel Rivas Costa <miguel.rivas@quobis.es>

## Feedback-Chanel

- You may use the mailing list [sonata-dev@lists.atosresearch.eu](mailto:sonata-dev@lists.atosresearch.eu)
* [GitHub issues](https://github.com/sonata-nfv/tng-sdk-validation/issues)
