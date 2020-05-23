#!/bin/bash

USAGE="./launchWorker.sh [--cffs]
    launch the lambda worker docker container. If the cffs option is passed, the lambda will attempt to mount cffs instead of docker directly mounting the cffsProj directory as a volume." 

if [ $# == 1 ]; then
    if [ $1 == "--cffs" ]; then
        CFFSVOL=""
    else
        echo "Only supported argument is 'cffs'"
    fi
else
    CFFSVOL="-v $(pwd)/..:/tmp/cffs"
fi

docker run --rm  \
  --network=pysatnet \
  --name=lambda01 \
  -e DOCKER_LAMBDA_STAY_OPEN=1 \
  -p 9001:9001 \
  -v $(pwd)/lambda:/var/task:ro,delegated \
  $CFFSVOL \
  lambci/lambda:python3.7 \
  handler.lambda_handler
