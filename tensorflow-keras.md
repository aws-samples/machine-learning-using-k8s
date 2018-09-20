# TensorFlow and Keras on Amazon EKS

This document exaplins how to run a TensorFlow and Keras sample on Amazon EKS. It requires to setup KubeFlow as explained in [KubeFlow on Amazon EKS](kubeflow.md).

[Keras](https://keras.io/) is a high-level API with readymade networks that can run on TensorFlow.

## MNIST training using TensorFlow on EKS

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

1. Build a docker image with MNIST source code and installation. Use the Dockerfile in `tensorflow/mnist/Dockerfile` to use it.

   ```
   docker image build tensorflow/mnist -t <tag_for_image>
   ```

   This will generate a docker image which will have all the utility to run MNIST. You can push this generated image to docker hub in your personal repo. For convenience, a docker image is already pushed in the docker hub `rgaut/deeplearning-tensorflow:with_tf_keras`.

2. Create a pod which will use this docker image and runs the MNIST training. The pod file is available at `tensorflow/mnist/tensorflow.yaml`

   ```
   kubectl create -f samples/tensorflow/mnist/tensorflow.yaml
   ```

   At this point you have the pod running and training will start. You can check the status of pod by running `kubectl get pod tensorflow`.

3. Check the progress in training:

   ```
   	kubectl logs tensorflow
	Using TensorFlow backend.
	Downloading data from https://s3.amazonaws.com/img-datasets/mnist.npz

	   16384/11490434 [..............................] - ETA: 0s
	   24576/11490434 [..............................] - ETA: 41s
	   40960/11490434 [..............................] - ETA: 49s
	   73728/11490434 [..............................] - ETA: 41s
	   90112/11490434 [..............................] - ETA: 44s
	  122880/11490434 [..............................] - ETA: 40s
	  163840/11490434 [..............................] - ETA: 36s
	  212992/11490434 [..............................] - ETA: 32s
	  262144/11490434 [..............................] - ETA: 30s
	  335872/11490434 [..............................] - ETA: 26s
	  417792/11490434 [>.............................] - ETA: 23s
	  507904/11490434 [>.............................] - ETA: 21s
	  614400/11490434 [>.............................] - ETA: 18s
	  737280/11490434 [>.............................] - ETA: 16s
	  876544/11490434 [=>............................] - ETA: 15s
	 1015808/11490434 [=>............................] - ETA: 13s
	 1187840/11490434 [==>...........................] - ETA: 12s
	 1392640/11490434 [==>...........................] - ETA: 10s
	 1622016/11490434 [===>..........................] - ETA: 9s 
	 1884160/11490434 [===>..........................] - ETA: 8s
	 2211840/11490434 [====>.........................] - ETA: 7s
	 2564096/11490434 [=====>........................] - ETA: 6s
	 2981888/11490434 [======>.......................] - ETA: 5s
	 3465216/11490434 [========>.....................] - ETA: 4s
	 4038656/11490434 [=========>....................] - ETA: 3s
	 4718592/11490434 [===========>..................] - ETA: 3s
	 5529600/11490434 [=============>................] - ETA: 2s
	 6397952/11490434 [===============>..............] - ETA: 1s
	 7446528/11490434 [==================>...........] - ETA: 1s
	 8593408/11490434 [=====================>........] - ETA: 0s
	 9871360/11490434 [========================>.....] - ETA: 0s
	11378688/11490434 [============================>.] - ETA: 0s
	11493376/11490434 [==============================] - 3s 0us/step

	11501568/11490434 [==============================] - 3s 0us/step
	2018-09-19 10:12:36.083130: I tensorflow/core/platform/cpu_feature_guard.cc:141] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
	x_train shape: (60000, 28, 28, 1)
	60000 train samples
	10000 test samples
	Train on 60000 samples, validate on 10000 samples

	. . .

	59648/60000 [============================>.] - ETA: 0s - loss: 0.0263 - acc: 0.9917
	59776/60000 [============================>.] - ETA: 0s - loss: 0.0263 - acc: 0.9918
	59904/60000 [============================>.] - ETA: 0s - loss: 0.0263 - acc: 0.9918
	60000/60000 [==============================] - 31s 516us/step - loss: 0.0262 - acc: 0.9918 - val_loss: 0.0286 - val_acc: 0.9916
	Test loss: 0.028569993475805314
	Test accuracy: 0.9916
   ```

