#!/bin/bash

if [ -z "$CFFS_SRC" ]; then
    echo "Please source cffsProj/env.sh or set the $CFFS_SRC variable"
    exit 1
fi

if [ $# == 1 ]; then
    CMD=$1
else
    CMD=bash
fi

# ENTRY_ON_MANAGER=$(echo "$CFFS_MANAGER_SCRIPTS/managerEntry.sh" | sed -e "s:$CFFS_PROJ_ROOT:$CFFS_PROJ_MNT:g")
# XXX this isn't totally general
ENTRY_ON_MANAGER=$CFFS_PROJ_MNT/pysatServerless/managerScripts/managerEntry.sh

docker run -it --rm \
  --network=pysatnet \
  --name=manaager \
  -e CFFS_PROJ_MNT=$CFFS_PROJ_MNT \
  -v $(pwd)/..:$CFFS_PROJ_MNT \
  --user sbx_user1051 \
  --entrypoint="$ENTRY_ON_MANAGER" \
  lambci/lambda:build-python3.7 $CMD
