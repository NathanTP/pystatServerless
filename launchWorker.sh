#!/bin/bash

docker run --rm  \
  --network=pysatnet \
  --name=lambda01 \
  -e DOCKER_LAMBDA_STAY_OPEN=1 \
  -p 9001:9001 \
  -v $(pwd)/lambda:/var/task:ro,delegated \
  -v $(pwd)/..:/tmp/cffs \
  lambci/lambda:python3.7 \
  handler.lambda_handler
