# Inference of MNIST using MXNet on Amazon EKS

This document explains how to perform inference of MNIST model using MXNet on Amazon EKS.

## Pre-requisite

Create [EKS cluster using GPU](../../eks-gpu.md).

## Upload model

1. If you've gone through the [Training MNIST using MXNet on Amazon EKS](../training/mxnet.md), a model is already stored in the identified S3 bucket. If so, then you can skip rest of this section.

1. If you've not done the training, a pre-trained model is already available at `samples/mnist/training/mxnet/saved_model`. This model requires your inference cluster has GPU. Use an S3 bucket in your region and upload this model:

   ```
   cd samples/mnist/training/mxnet/saved_model
   aws s3 sync . s3://your_bucket/mnist/mxnet_saved_model/
   ```

## Install MXNet Model Server

[MXNet Model Server](https://github.com/awslabs/mxnet-model-server) is a flexible and easy to use tool for serving deep learning models exported from MXNet or the Open Neural Network Exchange (ONNX).

1. Install Java:

	```
	brew tap caskroom/versions
	brew update
	brew cask install java8
	```

1. Install MXNet Model Server for CPU inference:

   ```
   pip install mxnet-mkl --user
   ```

1. WHAT NEXT?
