import base64
import boto3

import json
import cloudpickle 
import sys

from botocore import UNSIGNED
from botocore.config import Config


class Pool:
    def __init__(self, processes):
        _ = processes

    def starmap(self, func, iterable, chunksize=None):
        client = boto3.client('lambda', endpoint_url='http://lambda01:9001', config=Config(signature_version=UNSIGNED))

        results = []
        for arg in iterable:
            payload = {
                'Function': base64.b64encode(cloudpickle.dumps(func)).decode('utf-8'),
                'Arguments': base64.b64encode(cloudpickle.dumps(arg)).decode('utf-8')
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
            results.append(cloudpickle.loads(base64.b64decode(respPayload['Result'].encode('utf-8'))))

        return results

    def map(self, func, iterable, chunksize=None):
        return self.starmap(func, [ [a] for a in iterable ], chunksize)
