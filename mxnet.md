# MXNet on Amazon EKS 

This document explains how to run MXNet training on [Amazon EKS](https://aws.amazon.com/eks/).

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](eks-gpu.md) ready.

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

## Single node MNIST training using MXNet on EKS

1. Build a docker image with MNIST source code and installation. Use the Dockerfile in `mxnet/mnist/Dockerfile` to use it.

   ```
   docker image build mxnet/mnist -t <tag_for_image>
   ```

   This will generate a docker image which will have all the utility to run MNIST. You can push this generated image to docker hub in your personal repo. For convenience, A docker image is already pushed in the docker hub `rgaut/deeplearning-mxnet:with_mxnet`.

2. Create a pod which will use this docker image and runs the MNIST training. The pod file is available at `mxnet/mnist/mxnet.yaml`

   ```
   kubectl create -f mxnet/mnist/mxnet.yaml
   ```

   At this point you have the pod running and training will start. You can check the status of pod by running `kubectl get pod mxnet` 

3. Check the progress in training:

   ```
    kubectl logs mxnet
    INFO:root:start with arguments Namespace(add_stn=False, batch_size=64, disp_batches=100, dtype='float32', gc_threshold=0.5, gc_type='none', gpus=None, kv_store='device', load_epoch=None, lr=0.05, lr_factor=0.1, lr_step_epochs='10', model_prefix=None, mom=0.9, monitor=0, network='mlp', num_classes=10, num_epochs=20, num_examples=60000, num_layers=None, optimizer='sgd', test_io=0, top_k=0, wd=0.0001)
    DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): yann.lecun.com
    DEBUG:urllib3.connectionpool:http://yann.lecun.com:80 "GET /exdb/mnist/train-labels-idx1-ubyte.gz HTTP/1.1" 200 28881

    . . .

    INFO:root:Epoch[19] Batch [100] Speed: 59255.44 samples/sec accuracy=1.000000
    INFO:root:Epoch[19] Batch [200] Speed: 59155.16 samples/sec accuracy=0.999375
    INFO:root:Epoch[19] Batch [300] Speed: 59269.18 samples/sec accuracy=0.999687
    INFO:root:Epoch[19] Batch [400] Speed: 59127.79 samples/sec accuracy=0.999687
    INFO:root:Epoch[19] Batch [500] Speed: 59136.00 samples/sec accuracy=0.999687
    INFO:root:Epoch[19] Batch [600] Speed: 59191.81 samples/sec accuracy=0.999531
    INFO:root:Epoch[19] Batch [700] Speed: 59202.25 samples/sec accuracy=0.999687
    INFO:root:Epoch[19] Batch [800] Speed: 59169.37 samples/sec accuracy=1.000000
    INFO:root:Epoch[19] Batch [900] Speed: 59283.97 samples/sec accuracy=0.999844
    INFO:root:Epoch[19] Train-accuracy=0.999155
    INFO:root:Epoch[19] Time cost=1.016
    INFO:root:Epoch[19] Validation-accuracy=0.981688
   ```
