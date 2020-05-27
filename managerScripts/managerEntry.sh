#!/bin/bash
# This is run before whatever launchManager.sh is trying to run in order to get
# our standard environment variables all the time.
source $CFFS_PROJ_MNT/pysatServerless/env.sh
mkdir /tmp/cffs
exec $@
