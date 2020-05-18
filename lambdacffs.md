# Run in a Docker container

First, create the manager container. We will run all the commands to control
lambda from here. You can also run the manager from your own machine (at your
own risk). The rest of this document assumes that you are in the manager
container.

This document assumes that you use ../ as the main working directory for this
project. Feel free to place this extra data somewhere else.

```
docker network create -d bridge pysatnet
```

We can now launch the manager container:

```
./launchManager.sh
```

It has '..' mounted to '/tmp/cffs' for convenience. On a new clone you should
run '/tmp/cffs/pysatServerless/managerInit.sh' to create a virtual env for the
manager to use, along with any other files needed to run the example. You can
also delete the cffs/dockerSandbox directory and re-run managerInit.sh to clean
any cached state.

```
cd /tmp/cffs/pysatServerless
./managerInit.sh
source /tmp/cffs/dockerSandbox/sourceme.sh
```

Finally, we can run a manual local test to make sure everything works:

```
cd /tmp/cffs/pystatServerless
python3 seasonalOccurence.py -n 4 -p 2
```

This ran in your manager container and didn't use lambda at all.

# Getting it to work with a Lambda Docker image
To run using AWS lambda, we use the AWS-provided lambda docker image. This
image is able to emulate the AWS lambda service and can be used to test the API
locally.

## Start up the lambci environment
On your host, run the following commands to create and launch the lambda container.

The first step is to ensure that the lambda container has access to the
cloudpickle package (needed to exchange code/arguments with the driver
program).
```
cp -a ../dockerSandbox/env/lib/python3.7/site-packages/cloudpickle lambda
```

We can now launch the container using the 'launchWorker.sh' script:

```
./launchWorker.sh
```

Finally, we can run the application using our lambda container instead of local
processes. Back on your manager container, run seasonalOccurence.py with the '--lambda' option:

```
python3 seasonalOccurence.py -n 4 -p 2 --lambda
```

This time seasonalOccurence.py used lambdamultiprocessing instead of the
standard multiprocessing to run the function in lambda.

# Getting it to work with CFFS

```
export CFFS_BUILD={{PATH TO YOUR CFFS /build DIRECTORY}}
```

Start up a Docker instance running the transaction server.
```
docker run --rm  \
  --network=pysatnet \
  --name=txnserver \
  -v $CFFS_BUILD:/cffsbuild \
  lambci/lambda:build-provided \
  /cffsbuild/txnserver -address 0.0.0.0
```

Start up a Docker instance to run the Lambda function
```
docker run --rm  \
  --network=pysatnet \
  --name=lambda01 \
  -e DOCKER_LAMBDA_STAY_OPEN=1 \
  -p 9001:9001 \
  -v $(pwd)/lambda:/var/task:ro,delegated \
  -v $CFFS_BUILD/runtime-python37:/opt:ro,delegated \
  lambci/lambda:provided \
  handler.lambda_handler
```

Start up the Docker instance where you will run the script
```
docker run -it --rm \
  --network=pysatnet \
  -v $CFFS_BUILD/runtime-python37:/opt:ro,delegated \
  -v $(pwd)/..:/pysatnet:ro \
  --entrypoint=/bin/bash \
  lambci/lambda:provided \
```

Now, in the Docker container run

```
mkdir -p /tmp/cffs
export CFFS_MOUNT_POINT=/tmp/cffs
export LD_LIBRARY_PATH=/opt/lang/lib:$LD_LIBRARY_PATH


/opt/bin/cffssvc -mode txn -server txnserver:10000 &

LD_PRELOAD=cffs.so.3 /bin/bash 

mkdir -p /tmp/cffs/env/lib/python3.7/site-packages
cp -Rv /pysatnet/env/lib/python3.7/site-packages /tmp/cffs/env/lib/python3.7/

export PYTHONPATH=/tmp/cffs/env/lib/python3.7/site-packages
```

This command should be working but it isn't. We are having some problem importing packages. Note that if I configure it to import from `/pysatnet/env` it doesn't work either.

```
HOME=/tmp/cffs /opt/lang/bin/python3 /pysatnet/pystatServerless/seasonalOccurence.py  -n 10 -p 2
```
