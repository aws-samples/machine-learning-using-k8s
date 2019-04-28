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

1. Setup a virtual environment:

	```
	pip install virtualenv --user
	export PATH=~/Library/Python/2.7/bin:$PATH
	# create a Python2.7 virtual environment
	virtualenv -p /usr/bin/python /tmp/pyenv2
	# Enter this virtual environment
	source /tmp/pyenv2/bin/activate
	```

	Location of `virtualenv` binary may be different. This can be found using `pip show virtualenv` command.

1. Install MXNet Model Server for CPU inference:

   ```
   pip install mxnet-mkl
   ```

1. Install MXNet Model Server:

	```
	pip install mxnet-model-server
	```

1. Update `~/.keras/keras.json` so that it looks like:

	```
	{
	    "epsilon": 1e-07, 
	    "floatx": "float32", 
	    "image_data_format": "channels_last", 
	    "backend": "mxnet"
	}
	```

	This is to ensure that the `backend` is `mxnet` and `image_data_format` is `channels_last`.

1. Run MXNet Model Server:

	```
	mxnet-model-server \
	--start \
	--model-store ../../../samples/mnist/inference/mxnet/archived_model \
	--models mnist=mnist_cnn.mar
	```

1. Run inference server:

	```
	curl -X POST localhost:8080/predictions/mnist -T 9.png
	```

1. In a new terminal, run the inference:

	```
	curl -X POST localhost:8080/predictions/mnist -T 9.png
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
    100  8042  100    56  100  7986    747   104k --:--:-- --:--:-- --:--:--  103k
    Prediction is [9] with probability of 92.52161383628845%
	```

