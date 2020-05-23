#!/bin/bash
# This script is a helper script for runExperiment.sh and should never be run
# by itself

echo "Copying files to cffs: $SANDBOX"
cp -r $SANDBOX_CACHE/* $SANDBOX/
cp /tmp/cffs/cffsEnvActivate $SANDBOX/env/bin/activate
source $SANDBOX/env/bin/activate

HOME=$SANDBOX python3 seasonalOccurence.py -s $SANDBOX $TESTARGS

echo "done"
