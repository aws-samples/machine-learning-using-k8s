# Training MNIST using MXNet and Keras on Amazon EKS

This document explains how to build a MNIST model using MXNet and Keras on Amazon EKS.

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](eks-gpu.md) ready.

## MNIST Training using MXNet on EKS

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

1. You can use a pre-built Docker image `rgaut/deeplearning-mxnet:with_mnist_cnn_gpu`. This image uses `763104351884.dkr.ecr.us-east-1.amazonaws.com/mxnet-training:1.4.0-gpu-py27-cu90-ubuntu16.04` as the base image. It comes bundled with MXNet. It also has training code and downloads training and test data sets.

   Alternatively, you can build a Docker image using the Dockerfile in `samples/mnist/training/mxnet/Dockerfile`.

   ```
   docker image build samples/mnist/training/mxnet/ -t <tag_for_image>
   ```

   This will create a Docker image that will have all the utilities to run MNIST.

1. Create a pod that will use this Docker image and run the MNIST training:

   ```
   kubectl create -f samples/mnist/training/mxnet/mxnet.yaml
   ```

1. Check status of the pod:

   ```
   kubectl get pods -l app=mxnet
   NAME        READY   STATUS      RESTARTS   AGE
   mxnet-mnist   0/1     Completed   0          6m
   ```

1. Check the progress in training:

   ```
   kubectl logs mxnet-mnist

   Using MXNet backend
   Downloading data from https://s3.amazonaws.com/img-datasets/mnist.npz
   
      16384/11490434 [..............................] - ETA: 0s
      24576/11490434 [..............................] - ETA: 35s
      57344/11490434 [..............................] - ETA: 30s
     122880/11490434 [..............................] - ETA: 21s
     303104/11490434 [..............................] - ETA: 11s
     581632/11490434 [>.............................] - ETA: 7s 
    1187840/11490434 [==>...........................] - ETA: 3s
    2375680/11490434 [=====>........................] - ETA: 2s
    3948544/11490434 [=========>....................] - ETA: 1s
    5521408/11490434 [=============>................] - ETA: 0s
    7094272/11490434 [=================>............] - ETA: 0s
    8683520/11490434 [=====================>........] - ETA: 0s
   10256384/11490434 [=========================>....] - ETA: 0s
   11493376/11490434 [==============================] - 1s 0us/step
   
   11501568/11490434 [==============================] - 1s 0us/step
   /usr/local/lib/python2.7/dist-packages/keras/backend/mxnet_backend.py:96: UserWarning: MXNet Backend performs best with `channels_first` format. Using `channels_last` will significantly reduce performance due to the Transpose operations. For performance improvement, please use this API`keras.utils.to_channels_first(x_input)`to transform `channels_last` data to `channels_first` format and also please change the `image_data_format` in `keras.json` to `channels_first`.Note: `x_input` is a Numpy tensor or a list of Numpy tensorRefer to: https://github.com/awslabs/keras-apache-mxnet/tree/master/docs/mxnet_backend/performance_guide.md
     train_symbol = func(*args, **kwargs)

   . . .

   [23:25:30] src/operator/nn/./cudnn/./cudnn_algoreg-inl.h:97: Running performance tests to find the best convolution algorithm, this can take a while... (setting env variable MXNET_CUDNN_AUTOTUNE_DEFAULT to 0 to disable)
   x_train shape: (60000, 28, 28, 1)
   60000 train samples
   10000 test samples
   Train on 60000 samples, validate on 10000 samples
   Epoch 1/12
   
     128/60000 [..............................] - ETA: 15:12 - loss: 2.3015 - acc: 0.1094
     384/60000 [..............................] - ETA: 5:15 - loss: 2.2646 - acc: 0.1667 
     640/60000 [..............................] - ETA: 3:14 - loss: 2.2128 - acc: 0.2437
     896/60000 [..............................] - ETA: 2:22 - loss: 2.1461 - acc: 0.2824
    1152/60000 [..............................] - ETA: 1:53 - loss: 2.0702 - acc: 0.3229
    1408/60000 [..............................] - ETA: 1:34 - loss: 1.9679 - acc: 0.3629
    1664/60000 [..............................] - ETA: 1:22 - loss: 1.8818 - acc: 0.3930
    1920/60000 [..............................] - ETA: 1:12 - loss: 1.8086 - acc: 0.4104
    2176/60000 [>.............................] - ETA: 1:05 - loss: 1.7239 - acc: 0.4370
   . . .
   59776/60000 [============================>.] - ETA: 0s - loss: 0.0398 - acc: 0.9882
   60000/60000 [==============================] - 14s 232us/step - loss: 0.0398 - acc: 0.9882 - val_loss: 0.0262 - val_acc: 0.9904
   Test loss: 0.026189500172245608
   Test accuracy: 0.9904
   MXNet Backend: Successfully exported the model as MXNet model!
   MXNet symbol file -  mnist_cnn-symbol.json
   MXNet params file -  mnist_cnn-0000.params
   
   . . .

   Model input data_names and data_shapes are: 
   data_names :  ['/conv2d_1_input1']
   data_shapes :  [DataDesc[/conv2d_1_input1,(128L, 28L, 28L, 1L),float32,NCHW]]
   
   . . .
   
   Note: In the above data_shapes, the first dimension represent the batch_size used for model training. 
   You can change the batch_size for binding the module based on your inference batch_size.
   ```

   Complete [detailed logs](mxnet_logs.txt).

   A copy of the model is also saved at `samples/mnist/training/mxnet/saved_model`.

## What happened?

- Runs `python /tmp/mnist_cnn.py` command (specified in the Dockerfile and available at samples/mnist/training/mxnet/mnist_cnn.py)
  - Downloads MNIST training and test data set from S3.
    - Each set has images and labels that identify the image
  - Performs supervised learning
    - Run 12 epochs using the training data with the specified parameters
    - For each epoch
      - Reads the training data
      - Builds the training model using the specified algorithm
      - Feeds the test data and matches with the expected output
      - Reports the accuracy, expected to improve with each run
    - Exports the trained model in `/mnist_model` directory at a worker node. The model consists of `mnist_cnn-0000.params` and `mnist_cnn-symbol.json` files. These are needed for inference.

