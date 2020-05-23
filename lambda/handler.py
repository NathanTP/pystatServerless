import base64
import cloudpickle
import os
import sys
import shutil
import pathlib
import subprocess as sp
import multiprocessing as mp
import contextlib

# Increases verbosity and degree of error checking
debug = True

cffsMnt = pathlib.Path("/tmp/cffs/cffsSandbox")
rootDir = cffsMnt
sys.path.append(str(rootDir / "env/lib/python3.7/site-packages"))
os.environ["HOME"] = str(rootDir)
cffsEnv = os.environ.copy()


def mountCffs(mntDir):
    """Launch the CFFS management daemon and configure it to mount at mntDir.
    In order for a process to actually see the mounted directory, it will need
    to be run with cffsRun()."""

    cffsTools = pathlib.Path("/var/task/cffsTools")
    cffsEnv['LD_LIBRARY_PATH'] = str(cffsTools) + ":" + cffsEnv['LD_LIBRARY_PATH']
    cffsEnv["CFFS_MOUNT_POINT"] = str(rootDir)

    if debug:
        cffsEnv["CFFS_VERBOSE"] = "1"

    return sp.Popen([cffsTools / "cffssvc", "-mode", "txn", "-server", "txnserver:10000"], env=cffsEnv)


@contextlib.contextmanager
def setenv(newEnv):
    orig = os.environ.copy()
    os.environ = (newEnv)
    try:
        yield
    finally:
        os.environ = orig


def cffsRun(f, **fargs):
    """Run the callable "f" with args "fargs", with CFFS available to it.
    Returns the return value of f. Note that f is run using multiprocessing and
    shares all the same restrictions regarding communication."""
    q = mp.Queue()
    def retProc(q, f, fargs):
        r = f(*fargs)
        q.put(r)

    with setenv(cffsEnv):
        p = mp.Process(target=retProc, args=[q, f, fargs])
        p.start()

    r = q.get()
    p.join()
    return r


# If the rootDir already exists, we're running in native filesystem mode (no
# CFFS). Otherwise we're running in CFFS mode and need to set up our
# filesystem before proceeding.
if not rootDir.exists():
    if debug:
        print("Project root dir does not exist: ", rootDir)
        print("Assuming CFFS is being used")

    cffsMnt.mkdir(mode=0o771)
    cffsProcess = mountCffs(cffsMnt)
    usingCffs = True
else:
    usingCffs = False

def lambda_handler(event, context):
    if debug:
        if usingCffs:
            if cffsProcess.poll():
                raise RuntimeError("cffssvc exited unexpectedly, lost cffs mount")

    f = cloudpickle.loads(base64.b64decode(event['Function'].encode('utf-8')))
    args = cloudpickle.loads(base64.b64decode(event['Arguments'].encode('utf-8')))
    if usingCffs:
        res = cffsRun(f, args)
    else:
        res = f(*args)

    return {
        'Result': base64.b64encode(cloudpickle.dumps(res)).decode('utf-8')
    }
