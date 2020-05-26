#!/bin/bash
set -e

USAGE="Usage: ./mountCffs.sh MOUNT_POINT"
# Mount cffs to the first argument and drop into a shell with access to that
# mount point.

if [[ $# == 0 ]]; then
    SANDBOX=$CFFS_PROJ_MNT/cffsSandbox
elif [[ $# != 1 ]]; then
    echo $USAGE
else
    SANDBOX=$1
    case "$SANDBOX" in
    */)
        echo "mount point has trailing slash, this probably won't do what you meant. Removing trailing slash:"
        SANDBOX=${SANDBOX%/}
        echo "New mount point: $SANDBOX"
        ;;
    esac
fi

export LD_LIBRARY_PATH=$CFFS_PROJ_MNT/cffs/build:$LD_LIBRARY_PATH
export CFFS_MOUNT_POINT=$SANDBOX

# Set to enable debugging
# export CFFS_VERBOSE=1
export INTERCEPT_LOG=/tmp/cffsLog-

if ! (ps -l | grep -q cffssvc); then
	$CFFS_PROJ_MNT/cffs/build/cffssvc -mode txn -server txnserver:10000 &
fi

LD_PRELOAD=cffs.so.3 bash
