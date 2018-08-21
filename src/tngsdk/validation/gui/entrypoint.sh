#!/bin/bash

# run son-validate service in background
export VAPI_CACHE_TYPE="simple"
# son-workspace --init
# son-validate-api  &
  tng-sdk-validate --api &
# serve web gui
http-server /home/dani/Documents/gui/dist/
