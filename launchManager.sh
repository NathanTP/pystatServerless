#!/bin/bash

if [ ! -d ../dockerSandbox ]; then
    mkdir ../dockerSandbox
    chmod -R 777 ../dockerSandbox
fi

docker run -it --rm \
  --network=pysatnet \
  -v $(pwd)/..:/tmp/cffs \
  --user sbx_user1051 \
  lambci/lambda:build-python3.7 bash
