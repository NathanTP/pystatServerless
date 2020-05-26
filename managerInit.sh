#!/bin/bash
# Usage: ./managerInit.sh [path/to/sandbox]
#   sandbox defaults to $CFFS_PROJ_MNT/dockerSandbox and must already exist

if [ $# == 1 ]; then
    SANDBOX=$1
else
    SANDBOX=$CFFS_SANDBOX_CACHE
fi

if [ ! -d $SANDBOX ]; then
    echo "Sandbox directory $SANDBOX not found"
    echo "Sandbox needs to be created on host with 777 permissions"
    exit 1
fi

cd $SANDBOX
export HOME=$SANDBOX

if [ ! -d $SANDBOX/env ]; then
    virtualenv --always-copy -p python3 ./env
    source env/bin/activate
    pip3 install numpy
    pip3 install pysat matplotlib cloudpickle boto3

    # XXX This was needed once, why not anymore?
    # mkdir -p lib
    # cp ./env/lib/python3.7/site-packages/numpy.libs/* ./lib/
fi

mkdir -p datasets

echo "source $SANDBOX/env/bin/activate" > $SANDBOX/sourceme.sh
echo "export HOME=$SANDBOX/" >> $SANDBOX/sourceme.sh

echo "Done, please source $SANDBOX/sourceme.sh"
