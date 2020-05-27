#!/bin/bash

# USAGE: ./runTest.sh [ARGS]
#   You must set $SANDBOX to the sandbox directory to run from
#   If you pass ARGS they will be used for the
#   seaosonalOccurences.py script, otherwise a modest default will
#   be used.

if [[ $# > 0 ]]; then
    TESTARGS=$@
else
    TESTARGS="-n 2 -p 2"
fi

source $SANDBOX/env/bin/activate
PYTHONPATH=$SANDBOX/env/lib/python3.7/site-packages:$SANDBOX/env/lib64/python3.7/site-packages HOME=$SANDBOX python3 seasonalOccurence.py -s $SANDBOX $TESTARGS
