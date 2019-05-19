# Training MNIST using PyTorch on Amazon EKS

This document explains how to build a MNIST model using PyTorch on Amazon EKS.

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](../../eks-gpu.md) ready.

## MNIST training using PyTorch on EKS

This guide uses the [MNIST](https://en.wikipedia.org/wiki/MNIST_database)) which contains a training set of 60,000 examples, and a test set of 10,000 examples.

1. You can use a pre-built Docker image `seedjeffwan/pytorch-dist-mnist-test:1.10`. This image uses `pytorch/pytorch:1.0-cuda10.0-cudnn7-runtime` as the base image. It comes bundled with PyTorch. It also has training code and downloads training and test data sets. It also stores the model using a volume mount `/mount`. This maps to `/tmp` directory on the worker node.

   Alternatively, you can build a Docker image using the Dockerfile in `samples/mnist/training/pytorch/Dockerfile` to build it:

   ```
   docker build -t <dockerhub_username>/<repo_name>:<tag_name> .
   ```

2. Create a pod that will use this Docker image and run the MNIST training. First, the following changes need to be made in the manifest at `samples/mnist/training/pytorch/pytorch_mnist_example.yaml`:

   ```
   kubectl create -f samples/mnist/training/pytorch/pytorch_mnist_example.yaml
   ```

   This will start the pod and start the training. Check status:

   ```
   kubectl get pods
   NAME                               READY   STATUS    RESTARTS   AGE
   pytorch-dist-mnist-gloo-master-0   1/1     Running   0          5s
   pytorch-dist-mnist-gloo-worker-0   1/1     Running   0          3s
   ```

3. Check the progress in training:

	```
	kubectl logs -f pytorch-dist-mnist-gloo-master-0
  Using CUDA
  Using distributed PyTorch with gloo backend
  Downloading http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz
  Downloading http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz
  Downloading http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz
  Downloading http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz
  Processing...
  Done!
  Train Epoch: 1 [0/60000 (0%)]	loss=2.3000
  Train Epoch: 1 [640/60000 (1%)]	loss=2.2135
  Train Epoch: 1 [1280/60000 (2%)]	loss=2.1705
  Train Epoch: 1 [1920/60000 (3%)]	loss=2.0767
  Train Epoch: 1 [2560/60000 (4%)]	loss=1.8682
  Train Epoch: 1 [3200/60000 (5%)]	loss=1.4141
  ......
  ......
  Train Epoch: 1 [56960/60000 (95%)]	loss=0.0755
  Train Epoch: 1 [57600/60000 (96%)]	loss=0.1176
  Train Epoch: 1 [58240/60000 (97%)]	loss=0.1918
  Train Epoch: 1 [58880/60000 (98%)]	loss=0.2067
  Train Epoch: 1 [59520/60000 (99%)]	loss=0.0639

  accuracy=0.9659
	```

## What happened?

- Runs `mnist.py` command (specified in the `ENTRYPOINT` at Dockerfile and available at https://github.com/aws-samples/machine-learning-using-k8s/blob/master/samples/mnist/training/pytorch/Dockerfile)
  - Download MNIST training and test data set
    - Each set has images and labels that identify the image
  - Performs supervised learning
    - Run 10 epochs using the training data with the specified parameters
    - For each epoch
      - Reads the training data
      - Builds the training model using the specified algorithm
      - Feeds the test data and matches with the expected output
      - Reports the accuracy, expected to improve with each run
  - Generated model is persisted to worker host `/tmp/mnist_cnn.pt`.
