# Training MNIST using MXNet on Amazon EKS

This document explains how to build a MNIST model using MXNet on Amazon EKS.

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](eks-gpu.md) ready.

## MNIST Training using MXNet on EKS

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

1. You can use a pre-built Docker image `rgaut/deeplearning-mxnet:with_mxnet`. This image uses `763104351884.dkr.ecr.us-east-1.amazonaws.com/mxnet-training:1.4.0-gpu-py27-cu90-ubuntu16.04` as the base image. It comes bundled with MXNet. It also has training code and downloads training and test data sets.

   Alternatively, you can build a Docker image using the Dockerfile in `samples/mxnet/mnist/Dockerfile`.

   ```
   docker image build samples/mxnet/mnist -t <tag_for_image>
   ```

   This will create a Docker image that will have all the utilities to run MNIST.

1. Create a pod that will use this Docker image and run the MNIST training:

   ```
   kubectl create -f samples/mxnet/mnist/mxnet.yaml
   ```

   To use GPU for training you can run the following command:

   ```
   kubectl create -f samples/mxnet/mnist/mxnet-gpu.yaml
   ```

   The second version includes `--gpus 0` as a command line paramter to the MNIST script.

1. Check status of the pod:

   ```
   kubectl get pods -l app=mxnet
   NAME        READY   STATUS      RESTARTS   AGE
   mxnet-gpu   0/1     Completed   0          6m
   ```

1. Check the progress in training:

   ```
   kubectl logs mxnet-gpu
   INFO:root:start with arguments Namespace(add_stn=False, batch_size=64, disp_batches=100, dtype='float32', gc_threshold=0.5, gc_type='none', gpus='0', kv_store='device', load_epoch=None, lr=0.05, lr_factor=0.1, lr_step_epochs='10', model_prefix=None, mom=0.9, monitor=0, network='mlp', num_classes=10, num_epochs=20, num_examples=60000, num_layers=None, optimizer='sgd', test_io=0, top_k=0, wd=0.0001)
   DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): yann.lecun.com
   DEBUG:urllib3.connectionpool:http://yann.lecun.com:80 "GET /exdb/mnist/train-labels-idx1-ubyte.gz HTTP/1.1" 200 28881

   . . .

   INFO:root:Epoch[19] Batch [800] Speed: 62175.69 samples/sec accuracy=1.000000
   INFO:root:Epoch[19] Batch [900] Speed: 62016.67 samples/sec accuracy=0.999687
   INFO:root:Epoch[19] Train-accuracy=0.999578
   INFO:root:Epoch[19] Time cost=0.969
   INFO:root:Epoch[19] Validation-accuracy=0.982683
   ```

## What happened?

- Runs `/root/incubator-mxnet/example/image-classification/train_mnist.py` command (specified in the Dockerfile and available at https://github.com/apache/incubator-mxnet/blob/master/example/image-classification/train_mnist.py)
  - Downloads MNIST training and test data set
    - Each set has images and labels that identify the image
  - Performs supervised learning
    - Run 20 epochs using the training data with the specified parameters
    - For each epoch
      - Reads the training data
      - Builds the training model using the specified algorithm
      - Feeds the test data and matches with the expected output
      - Reports the accuracy, expected to improve with each run

