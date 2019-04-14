# Training MNIST using TensorFlow and Keras on Amazon EKS

This document exaplins how to build a MNIST model using TensorFlow and Keras on Amazon EKS.

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](eks-gpu.md) ready.

## MNIST training using TensorFlow on EKS

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

1. You can use a pre-built Docker image `rgaut/deeplearning-tensorflow:with_model`. This image uses `tensorflow/tensorflow` as the base image. It comes bundled with TensorFlow. It also has training code and downloads training and test data sets. It also stores the model using a volume mount `/mount`. This maps to `/tmp` directory on the worker node.

   Alternatively, you can build a Docker image using the Dockerfile in `samples/mnist/training/tensorflow/Dockerfile` to build it. This Dockerfile uses [AWS Deep Learning Containers](https://aws.amazon.com/machine-learning/containers/). Accessing this image requires that you login to the ECR repository:

   ```
   $(aws ecr get-login --no-include-email --region us-east-1 --registry-ids 763104351884)
   ```

   Then the Docker image can be built:

   ```
   docker build -t <dockerhub_username>/<repo_name>:<tag_name> .
   ```

   This will create a Docker image that will have all the utilities to run MNIST.

2. Create a pod that will use this Docker image and run the MNIST training:

   Change S3 saved model and summary path and they will be used in following serving and tensorboard section.
   You also need to make sure you create a `aws-secret` for tensorflow to authenticate s3 service.

   ```
   kubectl create -f samples/mnist/training/tensorflow/mnist_train.yaml
   ```

   This will start the pod and start the training. Check status:

   ```
   kubectl get pod tensorflow -w
   NAME                     READY   STATUS    RESTARTS   AGE
   mnist-tensorflow-keras   1/1     Running   0          25s
   ```


3. Check the progress in training:

	```
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

  60000/60000 [==============================] - 5s 90us/sample - loss: 0.5394 - acc: 0.8131
  Epoch 2/10
  60000/60000 [==============================] - 5s 89us/sample - loss: 0.3892 - acc: 0.8617
  Epoch 3/10
  60000/60000 [==============================] - 5s 89us/sample - loss: 0.3571 - acc: 0.8724
  Epoch 4/10

	. . .

	Test accuracy: 0.880800008774
  Saved model: s3://kubeflow-pipeline-data/mnist/export/1
	```

## What happened?

TODO:(@arun-gupta) Can you help update this section? Users can pass summary and saved model path, epochs is also configurable.
source: https://www.tensorflow.org/tfx/serving/tutorials/Serving_REST_simple

- Runs `/tmp/models/official/mnist/mnist.py` command (specified in the Dockerfile and available at https://github.com/tensorflow/models/blob/master/official/mnist/mnist.py)
  - Downloads MNIST training and test data set
    - Each set has images and labels that identify the image
  - Performs supervised learning
    - Run 40 epochs using the training data with the specified parameters
    - For each epoch
      - Reads the training data
      - Builds the training model using the specified algorithm
      - Feeds the test data and matches with the expected output
      - Reports the accuracy, expected to improve with each run
  	- A checkpoint is saved every 600 seconds
  - Generated model is persisted using a volume mount `/mount`. This maps to `/tmp` directory on the worker node. The output shows the model is saved to `/model/temp-1554929937/saved_model.pb`. This would map to `/tmp/1554929937` directory. Copy this model from the worker node:

  ```
  scp -i ~/.ssh/arun-us-west2.pem -r ec2-user@ec2-54-149-89-246.us-west-2.compute.amazonaws.com:/tmp/1554929937 .
  ```

  Note, you may have to try this command on different worker nodes as the training pod might have run on any of the worker nodes. More details about logging in to the EKS worker nodes is at http://arun-gupta.github.io/login-eks-worker/.


