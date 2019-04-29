# Inference of MNIST using MXNet on Amazon EKS

This document explains how to perform inference of MNIST model using [Apache MXNet Model Server](https://github.com/awslabs/mxnet-model-server) (MMS). MMS is a flexible and easy to use tool for serving deep learning models trained by MXNet.

TODO: Convert these steps to use Amazon EKS. [https://github.com/aws-samples/machine-learning-using-k8s/issues/88](#88)

## Pre-requisite (TODO)

Create [EKS cluster using GPU](../../eks-gpu.md).

## Install MXNet Model Server

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

## Prepare model archive

Model Archive is an artifact that MMS can consume natively. This archive package can be easily created with the trained artifacts. A copy of this archive is available at `samples/mnist/inference/archived_model/mnist_cnn.mar`.

Skip rest of the section if you are using the pre-generated archive. This section explains how to generate MMS archive from the artifacts produced by model training.

1. Two artifacts were generated at end of the training - symbols file (`mnist_cnn-symbol.json`) and a params file (`mnist_cnn-0000.params`). These artifacts are provided in the [saved_model](../../training/mxnet/saved_model) directory. Copy these artifacts to `/tmp/models` directory.

	```
	mkdir /tmp/models
	cp samples/mnist/training/mxnet/saved_model/mnist_cnn-* /tmp/models
	```

1. `model-archiver` tool is also installed as part of MMS installation. It can be manually installed:

	```
	pip install model-archiver
	```

1. Create a `model-store` location under `tmp`:

	```
	mkdir /tmp/model-store
	```

1. Copy the [../../../samples/mnist/inference/mxnet/mnist_cnn_inference.py](mnist_cnn_inference.py) to `/tmp/models` directory:

	```
	cp samples/mnist/inference/mxnet/mnist_cnn_inference.py /tmp/models
	```

1. Generate model archive:

	```
	model-archiver \
		--model-name mnist_cnn \
		--model-path /tmp/models \
		--export-path /tmp/model-store \
		--handler mnist_cnn_inference:handle -f
	```

	This command creates an model archive called `mnist_cnn.mar` under `/tmp/model-store`.

## Run inference

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
	--model-store samples/mnist/inference/mxnet/archived_model \
	--models mnist=mnist_cnn.mar
	```

	The above command creates an endpoint called `mnist`.

	If you generated your own archive at `/tmp/model-store`, then make sure to specify that directory as parameter to `--model-store`.

1. In a new terminal, run the inference:

	```
	curl -X POST localhost:8080/predictions/mnist -T samples/mnist/inference/mxnet/utils/9.png
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
    100  8042  100    56  100  7986   3105   432k --:--:-- --:--:-- --:--:--  458k
    Prediction is [9] with probability of 92.52161979675293%
	```

	Run another inference:

	```
	curl -X POST localhost:8080/predictions/mnist -T samples/mnist/inference/mxnet/utils/7.jpg
	  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
	                                 Dload  Upload   Total   Spent    Left  Speed
	100   608  100    52  100   556    568   6081 --:--:-- --:--:-- --:--:--  6109
	Prediction is [7] with probability of 99.9999761581%
	```

