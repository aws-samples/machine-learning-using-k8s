# MXNet on Amazon EKS 

This document explains how to run MXNet training on [Amazon EKS](https://aws.amazon.com/eks/).

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](eks-gpu.md) ready.

## MNIST training using MXNet on EKS

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

1. You can use a pre-built Docker image `rgaut/deeplearning-mxnet:with_mxnet`. Alternatively, duild a docker image with MNIST source code and installation. Use the Dockerfile in `mxnet/mnist/Dockerfile` to use it.

   ```
   docker image build mxnet/mnist -t <tag_for_image>
   ```

   This will generate a docker image which will have all the utility to run MNIST. You can push this generated image to docker hub in your personal repo.

1. Create a pod that will use this docker image and run the MNIST training:

   ```
   kubectl create -f samples/mxnet/mnist/mxnet.yaml
   ```

   To use GPU for training you can run below command

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

   TODO: Explain the results.