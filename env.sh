export CFFS_PROJ_ROOT=$(readlink -f $(dirname $BASH_SOURCE))

if [[ -z $CFFS_BUILD ]]; then
  export CFFS_BUILD=$CFFS_PROJ_ROOT/../cffs/build
fi

export CFFS_HOST_SCRIPTS=$CFFS_PROJ_ROOT/hostScripts
export CFFS_MANAGER_SCRIPTS=$CFFS_PROJ_ROOT/managerScripts

# This is where CFFS_PROJ_ROOT gets mounted on docker images. CFFS_PROJ_ROOT
# will point here if on docker, otherwise it will point to whereever cffsProj
# is cloned on your host.
if [[ -z $CFFS_PROJ_MNT ]]; then
  export CFFS_PROJ_MNT=/tmp/proj
fi

# Various sandboxes for different cases

# Default mount point for cffs
if [[ -z $CFFS_MOUNT_POINT ]]; then
  export CFFS_MOUNT_POINT=/tmp/cffs
fi

# Used as baseline 
export CFFS_BASE_SANDBOX=$CFFS_PROJ_ROOT/sandboxes/baseSandbox

# Cached sandbox (copied into either CFFS_MOUNT_POINT or CFFS_BASE_SANDBOX for
# tests).
export CFFS_SANDBOX_CACHE=$CFFS_PROJ_ROOT/sandboxes/sandboxCache
