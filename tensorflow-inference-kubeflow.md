# Tensorflow Serving on Amazon EKS using Kubeflow
This document explains how to perform Tensorflow inference on [Amazon EKS](https://aws.amazon.com/eks/) using Kubeflow

## Prerequisite
1. Create [EKS cluster using GPU](eks-gpu.md)
2. Install [Kubeflow](kubeflow.md)
3. Basic understanding of [TensorFlow Serving](https://www.tensorflow.org/serving/)
4. Prepare pretrained tensorflow model on [S3](#upload-pretrained-model-to-s3)

## Serve the Tensorflow model

1. Install Tensorflow Serving pkg
   ```
   ks pkg install kubeflow/tf-serving
   ```

2. Prepare kubernete secret to store your AWS Credential. Please check [document](aws-credential-secret.md). Remember secret name and data fields.

3. Install Tensorflow Serving AWS Component (Deployment + Service)
   ```
   export TF_SERVING_SERVICE=mnist-service
   export TF_SERVING_DEPLOYMENT=mnist

   ks generate tf-serving-service ${TF_SERVING_SERVICE}
   ks param set ${TF_SERVING_SERVICE} modelName ${TF_SERVING_DEPLOYMENT}    // match your deployment mode name
   ks param set ${TF_SERVING_SERVICE} serviceType ClusterIP    // optional, change type to LoadBalancer to expose external IP.

   ks generate tf-serving-deployment-aws ${TF_SERVING_DEPLOYMENT}
   ks param set ${TF_SERVING_DEPLOYMENT} modelBasePath s3://eks-tensorflow-model/mnist
   ks param set ${TF_SERVING_DEPLOYMENT} s3Enable true
   ks param set ${TF_SERVING_DEPLOYMENT} s3SecretName aws-s3-secret
   ks param set ${TF_SERVING_DEPLOYMENT} s3UseHttps true
   ks param set ${TF_SERVING_DEPLOYMENT} s3VerifySsl true
   ks param set ${TF_SERVING_DEPLOYMENT} s3AwsRegion us-west-2
   ks param set ${TF_SERVING_DEPLOYMENT} s3Endpoint s3.us-west-2.amazonaws.com

   ks param set ${TF_SERVING_DEPLOYMENT} numGpus 1
   ```
4. Deploy Tensorflow Serving components

   ```
   ks apply default -c ${TF_SERVING_SERVICE}
   ks apply default -c ${TF_SERVING_DEPLOYMENT}
   ```

5. If you use ClusterIP, forward port so you can test it locally

   ```
   kubectl port-forward -n kubeflow `kubectl get pods -n kubeflow --selector=app=mnist -o jsonpath='{.items[0].metadata.name}'` 8500:8500
   ```

6. Make prediction request. Check sample [mnist_input.json](samples/tensorflow-serving/mnist_input.json)

   ```
   $ curl -d @mnist_input.json   -X POST http://localhost:8500/v1/models/mnist:predict

   {
    "predictions": [
        {
            "classes": 5,
            "probabilities": [2.34393e-22, 1.37861e-16, 9.06871e-20, 2.48256e-05, 3.94171e-23, 0.999975, 3.54938e-20, 2.2284e-15, 1.07518e-12, 4.44746e-12]
        }
    ]
   }
   ```


### Upload pretrained model to S3

1. Download Tensorflow model and export saved model
   If you has GPU nodes, use
   ```
   nvidia-docker run -it -v /tmp/saved_model:/model tensorflow/tensorflow:1.12.0-gpu bash
   ```
   If you use CPU for serving, use

   ```
   docker run -it -v /tmp/saved_model:/model tensorflow/tensorflow:1.12.0 bash
   ```

   Then you will get into container, follow steps to dump your model.

   ```
   apt update && apt install git
   git clone -b r1.12.0 https://github.com/tensorflow/models.git /tmp/models

   export PYTHONPATH="$PYTHONPATH:/tmp/models"
   pip install --user -r /tmp/models/official/requirements.txt

   python /tmp/models/official/mnist/mnist.py --export_dir /model/
   exit
   ```
   Now we get model in Tensorflow SavedModel format in /tmp/saved_model on the host.
   ```
   .
   |-- saved_model.pb
   `-- variables
       |-- variables.data-00000-of-00001
       `-- variables.index
   ```

2. Create S3 bucket and upload your models to `s3://eks-tensorflow-model/mnist/1`. `1` is model version number. You can also use our pretrained model [here](samples/tensorflow-serving/model). This requires your serving component has GPU.
