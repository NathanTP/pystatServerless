#!/bin/bash
# This script assumes you've sourced cffsEvalScripts/cffsevalEnv.sh

if [ $# == 1 ]; then
    SANDBOX=$1
else
    SANDBOX=$CFFS_MOUNT_POINT
fi

$CFFS_MANAGER_SCRIPTS/managerInit.sh $CFFS_SANDBOX_CACHE

cp -r $CFFS_SANDBOX_CACHE/* $SANDBOX/
sed -E "s:$CFFS_SANDBOX_CACHE:$SANDBOX:g" $SANDBOX/env/bin/activate > /tmp/envActivate
cp /tmp/envActivate $SANDBOX/env/bin/activate
