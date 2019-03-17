# TensorFlow and Keras on Amazon EKS

This document exaplins how to run a TensorFlow and Keras sample on Amazon EKS. It requires to setup KubeFlow as explained in [KubeFlow on Amazon EKS](kubeflow.md).

[Keras](https://keras.io/) is a high-level API with readymade networks that can run on TensorFlow.

## MNIST training using TensorFlow on EKS

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

1. You can use a pre-built Docker image `rgaut/deeplearning-tensorflow:with_tf_keras`. Alternatively, build a docker image with MNIST source code and installation. Use the Dockerfile in `tensorflow/mnist/Dockerfile` to use it.

   ```
   docker image build tensorflow/mnist -t <dockerhub_username>/<repo_name>:<tag_name>
   ```

   This will generate a docker image which will have all the utility to run MNIST. You can push this generated image to docker hub in your personal repo.

2. Create a pod that will use this docker image and run the MNIST training. The pod file is available at `tensorflow/mnist/tensorflow.yaml`

   ```
   kubectl create -f samples/tensorflow/mnist/tensorflow.yaml
   ```

   At this point you have the pod running and training will start. Check the status of pod:

   ```
   kubectl get pod tensorflow
   ```

3. Check the progress in training:

	```
	Using TensorFlow backend.
	Downloading data from https://s3.amazonaws.com/img-datasets/mnist.npz

	   16384/11490434 [..............................] - ETA: 0s
	   24576/11490434 [..............................] - ETA: 36s
	   57344/11490434 [..............................] - ETA: 31s
	  122880/11490434 [..............................] - ETA: 21s
	  262144/11490434 [..............................] - ETA: 13s
	  557056/11490434 [>.............................] - ETA: 7s 
	 1171456/11490434 [==>...........................] - ETA: 4s
	 2301952/11490434 [=====>........................] - ETA: 2s
	 3874816/11490434 [=========>....................] - ETA: 1s
	 5464064/11490434 [=============>................] - ETA: 0s
	 7036928/11490434 [=================>............] - ETA: 0s
	 8609792/11490434 [=====================>........] - ETA: 0s
	10182656/11490434 [=========================>....] - ETA: 0s
	11493376/11490434 [==============================] - 1s 0us/step

	11501568/11490434 [==============================] - 1s 0us/step
	2019-03-17 20:48:25.236771: I tensorflow/core/platform/cpu_feature_guard.cc:141] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
	x_train shape: (60000, 28, 28, 1)
	60000 train samples
	10000 test samples
	Train on 60000 samples, validate on 10000 samples
	Epoch 1/12

	. . .

	59904/60000 [============================>.] - ETA: 0s - loss: 0.0274 - acc: 0.9918
	60000/60000 [==============================] - 31s 509us/step - loss: 0.0274 - acc: 0.9918 - val_loss: 0.0306 - val_acc: 0.9903
	Epoch 12/12

	  128/60000 [..............................] - ETA: 29s - loss: 0.0588 - acc: 0.9922
	  256/60000 [..............................] - ETA: 29s - loss: 0.0515 - acc: 0.9883	

	. . .

	59776/60000 [============================>.] - ETA: 0s - loss: 0.0271 - acc: 0.9919
	59904/60000 [============================>.] - ETA: 0s - loss: 0.0270 - acc: 0.9919
	60000/60000 [==============================] - 31s 510us/step - loss: 0.0270 - acc: 0.9919 - val_loss: 0.0264 - val_acc: 0.9915
	Test loss: 0.02641349581825889
	Test accuracy: 0.9915
	```

    TODO: Explain the results.
