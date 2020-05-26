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

if os.environ.get('USE_CFFS', "") != "":
    useCffs = True
else:
    useCffs = False

# This must match the manager because pysat saves certain paths
rootDir = pathlib.Path(os.environ['SANDBOX'])
sys.path.append(str(rootDir / "env/lib/python3.6/site-packages"))
sys.path.append(str(rootDir / "env/lib64/python3.6/site-packages"))
os.environ["HOME"] = str(rootDir)
cffsEnv = os.environ.copy()

if debug:
    print("Using sandbox: ", rootDir)
    print("cffs mode?: ",useCffs)
    print("sys path: ",sys.path)

def mountCffs(mntDir):
    """Launch the CFFS management daemon and configure it to mount at mntDir.
    In order for a process to actually see the mounted directory, it will need
    to be run with cffsRun()."""

    cffsTools = pathlib.Path("/var/task/cffsTools")
    cffsEnv['LD_LIBRARY_PATH'] = str(cffsTools) + ":" + cffsEnv['LD_LIBRARY_PATH']
    cffsEnv["CFFS_MOUNT_POINT"] = str(mntDir)

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


def cffsRun(f, *fargs):
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


if useCffs:
    if rootDir.exists():
        raise RuntimeError("sandbox directory ("+str(rootDir)+") already exists in cffs mode. Lambda expects to create this directory before mounting cffs.")

    rootDir.mkdir(mode=0o771, parents=True)
    if debug:
        print("Mounting cffs to",rootDir)
    cffsProcess = mountCffs(rootDir)


def runFuncEvent(event):
    f = cloudpickle.loads(base64.b64decode(event['Function'].encode('utf-8')))
    args = cloudpickle.loads(base64.b64decode(event['Arguments'].encode('utf-8')))
    return f(*args)


def lambda_handler(event, context):
    if debug:
        if useCffs:
            if cffsProcess.poll():
                raise RuntimeError("cffssvc exited unexpectedly, lost cffs mount")

    # cffsRun(testCffs)
    if useCffs:
        res = cffsRun(runFuncEvent, event)
    else:
        res = runFuncEvent(event) 

    return {
        'Result': base64.b64encode(cloudpickle.dumps(res)).decode('utf-8')
    }
