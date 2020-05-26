import base64
import boto3

import json
import cloudpickle 
import sys
import concurrent.futures

from botocore import UNSIGNED
from botocore.config import Config


class Pool:
    def __init__(self, processes):
        self.maxConcurrency = processes

    def starmap(self, func, iterable, chunksize=None):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.maxConcurrency) as executor:
            results = []
            futures = []
            for arg in iterable:
                # Each thread gets its own client (clients are not threadsafe)
                client = boto3.client('lambda', endpoint_url='http://lambda01:9001', config=Config(signature_version=UNSIGNED))
                payload = {
                    'Function': base64.b64encode(cloudpickle.dumps(func)).decode('utf-8'),
                    'Arguments': base64.b64encode(cloudpickle.dumps(arg)).decode('utf-8')
                }

                fut = executor.submit(client.invoke,
                    FunctionName='lambdamultiprocessing',
                    InvocationType='RequestResponse',
                    LogType='Tail',
                    Payload=json.dumps(payload)
                )
                futures.append(fut)

            for future in concurrent.futures.as_completed(futures):
                resp = future.result()

                if resp['StatusCode'] != 200:
                    print('Terminated in error')
                    sys.exit(1)

                respPayload = json.loads(resp['Payload'].read())
                results.append(cloudpickle.loads(base64.b64decode(respPayload['Result'].encode('utf-8'))))

        return results

    def map(self, func, iterable, chunksize=None):
        return self.starmap(func, [ [a] for a in iterable ], chunksize)
