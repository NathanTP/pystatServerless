#!/bin/bash
set -e

# Set up the host after a fresh clone, this should be idempotent
SANDBOX_CACHE=sandboxCache

# Docker networking
if ! docker network ls | grep -q "pysatnet"; then
    echo "Creating docker network 'pysatnet'"
    docker network create -d bridge pysatnet > /dev/null
fi

# Setup the manager docker image
if [ ! -d ../$SANDBOX_CACHE/env ]; then
    echo "Initializing the manager docker container"
    ./launchManager.sh /tmp/cffs/pysatServerless/managerInit.sh
fi

# Get the cloudpickle package into our lambda
if [ ! -d "lambda/cloudpickle" ]; then
    echo "Copying cloudpickle package from manager to lambda containers"
    cp -r ../$SANDBOX_CACHE/env/lib/python3.6/site-packages/cloudpickle lambda/
fi

# Lambda needs some shared libraries from the manager image
if [ ! -f lambda/lib/libgfortran.so.3 ] || [ ! -f lambda/lib/libquadmath.so.0 ]; then
    echo "Getting needed shared libraries from manager container"
    mkdir -p lambda/lib

    id=$(docker create jsssmith/cffs:build bash)
    docker cp -L $id:/usr/lib64/libgfortran.so.3 lambda/lib/
    docker cp -L $id:/usr/lib64/libquadmath.so.0 lambda/lib/
    docker rm -v $id > /dev/null
fi

# We need the cffs tools as well
if [ ! -f lambda/cffsTools ]; then
    if [ ! -d ../cffs/build ]; then
        echo "Please build cffs first"
        exit 1
    fi
    cp -r ../cffs/build lambda/cffsTools
fi

echo "Done! PySat example is ready to use"
