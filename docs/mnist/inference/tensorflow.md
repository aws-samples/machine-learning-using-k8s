# Inference of MNIST using TensorFlow on Amazon EKS

This document explains how to perform inference of MNIST model using TensorFlow on Amazon EKS.

## Pre-requisite

1. Create [EKS cluster using GPU](../../eks-gpu.md)
2. Install [Kubeflow](../../kubeflow.md)
3. Basic understanding of [TensorFlow Serving](https://www.tensorflow.org/serving/)
4. Prepare [pretrained tensorflow model](#upload-pretrained-model-to-s3) on S3

## Serve the TensorFlow model

1. Install TensorFlow Serving pkg:

   ```
   ks pkg install kubeflow/tf-serving
   ```

2. Prepare kubernete secret to store your AWS Credential. Please check [Store AWS Credentials in Kubernetes Secret](aws-credential-secret.md). Remember secret name and data fields.

3. Install Tensorflow Serving AWS Component (Deployment + Service):

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

## Upload pretrained model to S3

1. Get list of the nodes:

   ```
   kubectl get nodes
   NAME                                           STATUS   ROLES    AGE   VERSION
   ip-192-168-40-127.us-west-2.compute.internal   Ready    <none>   10m   v1.11.9
   ip-192-168-72-76.us-west-2.compute.internal    Ready    <none>   10m   v1.11.9
   ```

1. Get IP address of one of the worker nodes:

   ```
   aws ec2 describe-instances \
   --filters Name=private-dns-name,Values=ip-192-168-40-127.us-west-2.compute.internal \
   --query "Reservations[0].Instances[0].PublicDnsName" \
   --output text
   ```

1. Login to worker nodes:

   ```
   ssh -i ~/.ssh/arun-us-west2.pem ec2-user@<worker-ip>
   ```

1. Login to ECR:

   ```
   $(aws ecr get-login --no-include-email --region us-east-1 --registry-ids 763104351884)
   ```

   This is required to download [AWS Deep Learning Containers](https://aws.amazon.com/machine-learning/containers/).

1. Login to the Docker container.

   If you have GPU nodes in the cluster:

   ```
   nvidia-docker run -it -v /tmp/saved_model:/model 763104351884.dkr.ecr.us-east-1.amazonaws.com/tensorflow-inference:1.13-gpu-py27-cu100-ubuntu16.04 bash 
   ``` 

   Alternatively:

   ```
   nvidia-docker run -it -v /tmp/saved_model:/model tensorflow/tensorflow:1.12.0-gpu bash
   ```

   If you have CPU nodes in the cluster:

   ```
   docker run -it -v /tmp/saved_model:/model 763104351884.dkr.ecr.us-east-1.amazonaws.com/tensorflow-inference:1.13-cpu-py27-ubuntu16.04 bash 
   ```

   Alternatively:

   ```
   docker run -it -v /tmp/saved_model:/model tensorflow/tensorflow:1.12.0 bash
   ```

1. Export your model:

   ```
   apt update && apt install git
   git clone -b r1.12.0 https://github.com/tensorflow/models.git /tmp/models

   export PYTHONPATH="$PYTHONPATH:/tmp/models"
   pip install --user -r /tmp/models/official/requirements.txt

   python /tmp/models/official/mnist/mnist.py --export_dir /model/
   exit
   ```

   Now we get the model in Tensorflow's `SavedModel` format in `/tmp/saved_model` on the host.

   ```
   |-- saved_model.pb
   `-- variables
       |-- variables.data-00000-of-00001
       `-- variables.index
   ```

1. Create S3 bucket and upload your models to `s3://eks-tensorflow-model/mnist/1`. `1` is the model version number. You can also use our pretrained model [here](samples/tensorflow-serving/model). This requires your serving component has GPU.


