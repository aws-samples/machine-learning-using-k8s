# Inference with MXNet
Model Server for Apache MXNet (MMS) is a flexible and easy to use tool for serving deep learning models trained by MXNet.
For more details about this project refer to the [projects page](https://github.com/awslabs/mxnet-model-server).


# Using the model artifacts with MMS

The prerequisites to launch MMS on localhost with the trained MNIST artifacts are:

1. **Install MMS**
1. **Create model-archive**
1. **Launch the created model-archive onto MMS**
1. **Test your model by running inferences**

## Installing MMS:
Installing MMS is as easy as running a single command. MMS is distributed as a python package, hence the prerequisite 
to installing MMS is the `pip` (Package installer for Python).

```bash
$ pip install mxnet-model-server
```

This would install MMS on your host

## Creating model-archive
Model Archive is an artifact that MMS can consume natively. These archive packages can be easily created with the trained artifacts.
We got two artifacts at the end of the training, symbols file and a params file. Refer to [training/mxnet](../../training/mxnet) for training scripts.
The artifacts are provided in the [saved_model](../../training/mxnet/saved_model) directory.

**NOTE: For ease of use, we have provided the model-archive for the trained artifacts in [archived_model](archived_model) folder**

Let's create model archive.

1. Copy the trained model artifacts [mnist_cnn-0000.params](../../training/mxnet/saved_model/mnist_cnn-0000.params) 
and [mnist_cnn-symbol.json](../../training/mxnet/saved_model/mnist_cnn-symbol.json) to `/tmp/models` directory.
1. As a part of MMS installation, `model-archiver` tool is also installed. In case you want to install it manually, you could run
```bash
$ pip install model-archiver
```
1. Create a `model-store` location under `tmp`
```bash
$ mkdir /tmp/model-store
```
1. Copy the [mnist_cnn_inference.py](mnist_cnn_inference.py) to `/tmp/models` directory.
1. Run `model-archiver` as follows
```bash
$ model-archiver --model-name mnist_cnn --model-path /tmp/models --export-path /model-store --handler mnist_cnn_inference:handle -f
```
This command creates an model archive called `mnist_cnn.mar` under `/tmp/model-store`.

## Launch the created model-archive onto MMS

In the previous step we created a model archive. We can now launch this model archive onto MMS as follows

```bash
$ mxnet-model-server start --model-store /tmp/model-store --models mnist=mnist_cnn.mar 
``` 

The above command creates an endpoint called `mnist`.

## Test your model by running inference 
We have provided some sample images under [utils](utils) folder. We will use them to run inferences against the running MMS.

```bash
$ curl -X POST localhost:8080/predictions/mnist -T 7.jpg
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   600  100    44  100   556    347   4386 --:--:-- --:--:-- --:--:--  4412

Prediction is [7] with probability of 100.0%
```

MMS also provided containers and management API to launch the model-archives at run-time.