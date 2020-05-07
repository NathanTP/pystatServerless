import base64
import boto3

import json
import cloudpickle 
import sys

from botocore import UNSIGNED
from botocore.config import Config

client = boto3.client('lambda', endpoint_url='http://lambda01:9001', config=Config(signature_version=UNSIGNED))

def f(x):
    return x * x

payload = {
    'Function': base64.b64encode(cloudpickle.dumps(f)).decode('utf-8'),
    'Arguments': base64.b64encode(cloudpickle.dumps([2])).decode('utf-8')
}

resp = client.invoke(
    FunctionName='lambdamultiprocessing',
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=json.dumps(payload)
)

if resp['StatusCode'] != 200:
    print('Terminated in error')
    sys.exit(1)

respPayload = json.loads(resp['Payload'].read())
print(cloudpickle.loads(base64.b64decode(respPayload['Result'].encode('utf-8'))))