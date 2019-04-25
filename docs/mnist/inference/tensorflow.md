# Inference of MNIST using TensorFlow on Amazon EKS

This document explains how to perform inference of [Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist) model using TensorFlow and Keras on Amazon EKS.

## Pre-requisite

1. Create [EKS cluster using GPU](../../eks-gpu.md)
2. Install [Kubeflow](../../kubeflow.md)
3. Basic understanding of [TensorFlow Serving](https://www.tensorflow.org/serving/)

## Upload model

1. If you've gone through the [Training MNIST using TensorFlow and Keras on Amazon EKS](../training/tensorflow.md), a model is already stored in the identified S3 bucket. If so, then you can skip rest of this section.

1. If you've not done the training, a pre-trained model is already available at `samples/mnist/training/tensorflow/saved_model`. This model requires your inference cluster has GPU. Use an S3 bucket in your region and upload this model:

   ```
   cd samples/mnist/training/tensorflow/saved_model
   aws s3 sync . s3://your_bucket/mnist/tf_saved_model/
   ```

## Install TensorFlow Serving component

1. Install TensorFlow Serving package:

   ```
   cd ${KUBEFLOW_SRC}/${KFAPP}/ks_app
   ks pkg install kubeflow/tf-serving
   ```

1. Use [Store AWS Credentials in Kubernetes Secret](../../aws-creds-secret.md) to configure AWS credentials in your Kubernetes cluster with the name `aws-secret`. This needs to be created in the `kubeflow` namespace. So the command may look like:

   ```
   kubectl create -f secret.yaml -n kubeflow
   ```

1. Update `modelBasePath` below to match the S3 bucket name where the model is uploaded. Install Tensorflow Serving AWS Component (Deployment + Service):

   ```
   cd $KUBEFLOW_SRC/$KFAPP/ks_app
   export TF_SERVING_SERVICE=mnist-service
   export TF_SERVING_DEPLOYMENT=mnist

   ks generate tf-serving-service ${TF_SERVING_SERVICE}
   # match your deployment mode name
   ks param set ${TF_SERVING_SERVICE} modelName ${TF_SERVING_DEPLOYMENT}
   # optional, change type to LoadBalancer to expose external IP.
   ks param set ${TF_SERVING_SERVICE} serviceType ClusterIP

   ks generate tf-serving-deployment-aws ${TF_SERVING_DEPLOYMENT}
   # make sure to match the bucket name used for model
   ks param set ${TF_SERVING_DEPLOYMENT} modelBasePath s3://your_bucket/mnist/tf_saved_model
   ks param set ${TF_SERVING_DEPLOYMENT} s3Enable true
   ks param set ${TF_SERVING_DEPLOYMENT} s3SecretName aws-secret
   ks param set ${TF_SERVING_DEPLOYMENT} s3UseHttps true
   ks param set ${TF_SERVING_DEPLOYMENT} s3VerifySsl true
   ks param set ${TF_SERVING_DEPLOYMENT} s3AwsRegion us-west-2
   ks param set ${TF_SERVING_DEPLOYMENT} s3Endpoint s3.us-west-2.amazonaws.com

   ks param set ${TF_SERVING_DEPLOYMENT} numGpus 1
   ```

1. Deploy Tensorflow Serving components

   ```
   ks apply default -c ${TF_SERVING_SERVICE}
   ks apply default -c ${TF_SERVING_DEPLOYMENT}
   ```

1. Port forward inference endpoint for local testing:

   ```
   kubectl port-forward -n kubeflow `kubectl get pods -n kubeflow --selector=app=mnist -o jsonpath='{.items[0].metadata.name}' --field-selector=status.phase=Running` 8500:8500
   ```

1. Original datasets are feature vectors and we use `matplotlib` to draw picture to compare results. Install the following TensorFlow client-side components:

   ```
   pip install tensorflow matplotlib --user
   ```

1. Use the script [inference_client.py](../../../samples/mnist/inference/tensorflow/inference_client.py) to make prediction request. It will randomly pick one image from test dataset and make prediction.

   ```
   $ python inference_client.py --endpoint http://localhost:8500/v1/models/mnist:predict

    Data: {"instances": [[[[0.0], [0.0], [0.0], [0.0], [0.0] ... 0.0], [0.0]]]], "signature_name": "serving_default"}
    The model thought this was a Ankle boot (class 9), and it was actually a Ankle boot (class 9)
   ```

  ![inference-random-example](inference-random-example.png)

   Running this client shows an image and the output text indicates what kind of object it is.

1. Get serving pod:

   ```
   kubectl get pods -n kubeflow --selector=app=mnist --field-selector=status.phase=Running
   NAME                     READY   STATUS    RESTARTS   AGE
   mnist-7cc4468bc5-wm8kx   1/1     Running   0          2h
   ```

   Check the logs:

   ```
   kubectl logs mnist-7cc4468bc5-wm8kx -n kubeflow
   ```
