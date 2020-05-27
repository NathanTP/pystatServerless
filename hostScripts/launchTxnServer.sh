#!/bin/bash
set -e

if [ -z "$CFFS_SRC" ]; then
    echo "Please source env.sh (or set the CFFS environment variable to your cffs repo"
    exit 1
fi

docker run --rm  \
  --network=pysatnet \
  --name=txnserver \
  -v $CFFS_SRC/build:/cffsbuild \
  jsssmith/cffs:build \
  /cffsbuild/txnserver -address 0.0.0.0
  # /cffsbuild/txnserver -verbose -address 0.0.0.0
