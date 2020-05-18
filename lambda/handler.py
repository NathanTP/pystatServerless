import base64
import cloudpickle
import os
import sys

rootDir = "/tmp/cffs/dockerSandbox"
sys.path.append(rootDir + "/env/lib/python3.7/site-packages")
os.environ["LD_LIBRARY_PATH"] = rootDir + "/lib/:" + os.environ["LD_LIBRARY_PATH"]
os.environ["HOME"] = rootDir 

def lambda_handler(event, context):
    f = cloudpickle.loads(base64.b64decode(event['Function'].encode('utf-8')))
    args = cloudpickle.loads(base64.b64decode(event['Arguments'].encode('utf-8')))
    res = f(*args)
    return {
        'Result': base64.b64encode(cloudpickle.dumps(res)).decode('utf-8')
    }
