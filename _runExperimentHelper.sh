#!/bin/bash
# This script is a helper script for runExperiment.sh and should never be run
# by itself

echo "Copying files to cffs: $SANDBOX"
rm -rf $SANDBOX/*
rm -rf $SANDBOX/.*
cp -r $CFFS_SANDBOX_CACHE/* $SANDBOX/

# sed -i doesn't seem to work on cffs (can't create temp file) so we use shell
# redirects instead.
# sed -Ei "s:$SANDBOX_CACHE:$SANDBOX:g" $SANDBOX/env/bin/activate
sed -E "s:$CFFS_SANDBOX_CACHE:$SANDBOX:g" $SANDBOX/env/bin/activate > /tmp/envActivate
cp /tmp/envActivate $SANDBOX/env/bin/activate

source $SANDBOX/env/bin/activate

# cffs doesn't support symlinks, but python relies on relative paths to locate
# certain parts of PYTHONPATH, so we have to use the global python, but
# explicitly set PYTHONPATH to compensate.
PYTHONPATH=$SANDBOX/env/lib/python3.7/site-packages:$SANDBOX/env/lib64/python3.7/site-packages HOME=$SANDBOX python3 seasonalOccurence.py -s $SANDBOX $TESTARGS

echo "done"
