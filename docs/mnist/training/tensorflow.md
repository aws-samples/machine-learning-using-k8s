# Training MNIST using TensorFlow and Keras on Amazon EKS

This document explains how to build a Fashion MNIST model using TensorFlow and Keras on Amazon EKS.

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](../../eks-gpu.md) ready.

## MNIST training using TensorFlow on EKS

This guide uses the [Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist) which contains 70,000 grayscale images in 10 categories. This database is meant to be a drop-in replace of [MNIST](https://en.wikipedia.org/wiki/MNIST_database). The dataset consists of Zalando's article images.

1. You can use a pre-built Docker image `seedjeffwan/mnist_tensorflow_keras:1.13.1`. This image uses `tensorflow/tensorflow:1.13.1` as the base image. It comes bundled with TensorFlow. It also has training code and downloads training and test data sets. It also stores the model using a volume mount `/mount`. This maps to `/tmp` directory on the worker node.

   Alternatively, you can build a Docker image using the Dockerfile in `samples/mnist/training/tensorflow/Dockerfile` to build it:

   ```
   docker build -t <dockerhub_username>/<repo_name>:<tag_name> .
   ```

2. Create a pod that will use this Docker image and run the MNIST training. First, the following changes need to be made in the manifest at `samples/mnist/training/tensorflow/mnist_train.yaml`:

   1. Change the name of S3 bucket where data model would be saved. Specifically, the name `kubeflow-pipeline-data` should be updated to an S3 bucket in your account. This needs to be changed twice.
   1. This location is used later in serving the model and visualizing using TensorBoard.
   1. Use [Store AWS Credentials in Kubernetes Secret](../../aws-creds-secret.md) to configure AWS credentials in your Kubernetes cluster with the name `aws-secret`. Make sure to change the secret name to `aws-secret` instead of `aws-s3-secret`. Also, create the secret in default namespace:

   	  ```
   	  kubectl create -f secret.yaml
   	  ```

   Now, create the pod:


   ```
   kubectl create -f samples/mnist/training/tensorflow/mnist_train.yaml
   ```

   This will start the pod and start the training. Check status:

   ```
   kubectl get pods
   NAME                     READY   STATUS    RESTARTS   AGE
   mnist-tensorflow-keras   1/1     Running   0          47s
   ```

3. Check the progress in training:

	```
	kubectl logs mnist-tensorflow-keras
	Downloading data from https://storage.googleapis.com/tensorflow/tf-keras-datasets/train-labels-idx1-ubyte.gz
	32768/29515 [=================================] - 0s 1us/step
	40960/29515 [=========================================] - 0s 1us/step
	Downloading data from https://storage.googleapis.com/tensorflow/tf-keras-datasets/train-images-idx3-ubyte.gz
	26427392/26421880 [==============================] - 1s 0us/step
	26435584/26421880 [==============================] - 1s 0us/step
	Downloading data from https://storage.googleapis.com/tensorflow/tf-keras-datasets/t10k-labels-idx1-ubyte.gz

	. . .

	2019-04-16 03:22:04.767949: I tensorflow/core/platform/s3/aws_logging.cc:54] Found secret key
	2019-04-16 03:22:04.767983: I tensorflow/core/platform/s3/aws_logging.cc:54] Initializing CurlHandleContainer with size 25
	2019-04-16 03:22:04.768018: I tensorflow/core/platform/s3/aws_logging.cc:54] Found secret key

	. . .

	train_images.shape: (60000, 28, 28, 1), of float64
	test_images.shape: (10000, 28, 28, 1), of float64
	_________________________________________________________________
	Layer (type)                 Output Shape              Param #   
	=================================================================
	Conv1 (Conv2D)               (None, 13, 13, 8)         80        
	_________________________________________________________________
	flatten (Flatten)            (None, 1352)              0         
	_________________________________________________________________
	Softmax (Dense)              (None, 10)                13530     
	=================================================================
	Total params: 13,610
	Trainable params: 13,610
	Non-trainable params: 0
	_________________________________________________________________
	Epoch 1/10

	. . .

	60000/60000 [==============================] - 5s 76us/sample - loss: 0.5328 - acc: 0.8139
	Epoch 2/10

	. . .

	60000/60000 [==============================] - 4s 74us/sample - loss: 0.3939 - acc: 0.8621
	Epoch 3/10

	. . .

	Test accuracy: 0.876800000668

	Saved model: s3://eks-ml-example/mnist/export/1
	```

## What happened?

- Runs `mnist.py` command (specified in the `CMD` at Dockerfile and available at https://github.com/aws-samples/machine-learning-using-k8s/blob/master/samples/mnist/training/tensorflow/Dockerfile)
  - Download Keras-consumable MNIST-Fashion training and test data set
    - Each set has images and labels that identify the image
  - Performs supervised learning
    - Run 10 epochs using the training data with the specified parameters
    - For each epoch
      - Reads the training data
      - Builds the training model using the specified algorithm
      - Feeds the test data and matches with the expected output
      - Reports the accuracy, expected to improve with each run
  - Generated model is persisted to an S3 bucket specified in `mnist_train.yaml`.


