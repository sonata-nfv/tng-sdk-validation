# son-validator-gui

A visualization tool to view all errors and warnings resulting from a validation as well as the corresponding topology and forwarding graphs.

### Prerequisites

To build the validator GUI a few tools are necessary:
  * Node
  * npm (included with Node)

### Installing

No installation is necessary since it's a web GUI. Instead only a http server
is needed to host the static files after building it.

To build the application run the following commands at the root of gui repository:

```
   npm install request
   npm install
   npm install -g http-server
   npm run build:dev
```

Next run the script entrypoint.sh:
```
#!/bin/bash
# run tng-sdk-validate service in background
export VAPI_CACHE_TYPE="simple"
  tng-sdk-validate --api &
# serve web gui. here the path of dist should be specified
http-server /path_to_gui/gui/dist/

```


## Built With

* [AngularJS](https://angularjs.org/) - Web framework
* [D3js](https://d3js.org/) - Document manipulation library
* [Sass](http://sass-lang.com/) - CSS extension
* [Webpack 2](https://webpack.js.org/) - Javascript module bundler
