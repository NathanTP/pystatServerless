#!/bin/bash
set -e

# Mount cffs to the first argument and drop into a shell with access to that
# mount point.
USAGE='Usage: ./withCffs.sh CMD ...
  mounts CFFS to $CFFS_MOUNT_POINT and runs CMD with cffs enabled
'

if [[ -z $CFFS_MOUNT_POINT ]]; then
  echo "CFFS_MOUNT_POINT must be set"
  exit 1
fi

export LD_LIBRARY_PATH=$CFFS_SRC/build:$LD_LIBRARY_PATH

# Set to enable debugging
# export CFFS_VERBOSE=1
export INTERCEPT_LOG=/tmp/cffsLog-

if ! (ps -l | grep -q cffssvc); then
	$CFFS_BUILD/cffssvc -mode txn -server txnserver:10000 &
fi

LD_PRELOAD=cffs.so.3 $@
