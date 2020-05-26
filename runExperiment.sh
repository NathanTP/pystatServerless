#!/bin/bash
set -e

# We must call part of this script in a new process but it still needs the
# local variables, set -a basically auto-exports all variables.
set -a

# set -x
# Runs a default seasonalOcurence.py experiment.
# Usage: ./runExperiment.sh [--cffs] [ARGS]
#
# By default will use $CFFS_PROJ_MNT/dockerSandbox that is assumed to be a real
# (non-cffs) directory. You can optionally pass --cffs which will use
# $CFFS_PROJ_MNT/cffs/cffsSandbox which should be an empty directory. Running with cffs
# requires a working cffs txn server running. The local cffs daemon (cffssvc)
# will be launched and not killed after execution (to allow manual inspection
# after).
#
# You may optionally provide arguments to be passed to seasonalOccurence.py,
# these must come after the --cffs argument (if present).

# Set up the local container, note that this script should be idempotent and
# fast to rerun

if [[ $# > 0 ]] && [[ $1 == "--cffs" ]]; then
    echo "Using CFFS for experiment"
    SANDBOX=$CFFS_MOUNT_POINT

    export LD_LIBRARY_PATH=$CFFS_SRC/build:$LD_LIBRARY_PATH
    # export CFFS_VERBOSE=1
    export INTERCEPT_LOG=/tmp/cffsLog-
    # export INTERCEPT_ALL_OBJS=1

    USE_CFFS=true
    if ! (ps -l | grep -q cffssvc); then
        $CFFS_SRC/build/cffssvc -mode txn -server txnserver:10000 &
    fi

    shift
else
    # default
    SANDBOX=$CFFS_BASE_SANDBOX
    LD_PRELOAD=""
    USE_CFFS=false
fi

if [[ $# > 0 ]]; then
    TESTARGS=$@
else
    TESTARGS="-n 2 -p 2"
fi

if $USE_CFFS; then
    # LD_PRELOAD requires a new process, but I don't want to prefix every
    # command with it (plus builtins wouldn't use it), so we have a separate
    # script for the stuff that needs cffs. It's called funny because I don't
    # want to mark it executable and tempt users to call it directly which
    # will cause problems.
    LD_PRELOAD=cffs.so.3
else
    LD_PRELOAD=''
fi
./_runExperimentHelper.sh
