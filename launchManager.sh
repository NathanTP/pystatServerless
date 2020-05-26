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

docker run -it --rm \
  --network=pysatnet \
  --name=manaager \
  -e CFFS_PROJ_MNT=$CFFS_PROJ_MNT \
  -v $(pwd)/..:$CFFS_PROJ_MNT \
  --user sbx_user1051 \
  jsssmith/cffs:build $CMD
