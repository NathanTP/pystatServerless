import base64
import cloudpickle
import os
import sys
import shutil
import pathlib

rootDir = pathlib.Path("/tmp/cffs/dockerSandbox")
sys.path.append(str(rootDir / "env/lib/python3.7/site-packages"))
os.environ["HOME"] = str(rootDir)

def lambda_handler(event, context):
    f = cloudpickle.loads(base64.b64decode(event['Function'].encode('utf-8')))
    args = cloudpickle.loads(base64.b64decode(event['Arguments'].encode('utf-8')))
    res = f(*args)
    return {
        'Result': base64.b64encode(cloudpickle.dumps(res)).decode('utf-8')
    }
