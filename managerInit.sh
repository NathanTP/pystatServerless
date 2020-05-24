#!/bin/bash
# Usage: ./managerInit.sh [path/to/sandbox]
#   sandbox defaults to /tmp/cffs/dockerSandbox and must already exist

if [ $# == 1 ]; then
    SANDBOX=$1
else
    SANDBOX=/tmp/cffs/sandboxCache
fi

if [ ! -d $SANDBOX ]; then
    echo "Sandbox directory $SANDBOX not found"
    echo "Sandbox needs to be created on host with 777 permissions"
fi
cd $SANDBOX
export HOME=$SANDBOX

if [ ! -d $SANDBOX/env ]; then
    virtualenv -p python3 ./env
    source env/bin/activate
    pip3 install numpy
    pip3 install pysat matplotlib cloudpickle boto3

    # mkdir -p lib
    # cp ./env/lib/python3.7/site-packages/numpy.libs/* ./lib/
fi

mkdir -p datasets

echo "source $SANDBOX/env/bin/activate" > $SANDBOX/sourceme.sh
echo "export HOME=$SANDBOX/" >> $SANDBOX/sourceme.sh

echo "Done, please source $SANDBOX/sourceme.sh"
