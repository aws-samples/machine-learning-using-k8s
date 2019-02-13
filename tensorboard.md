# TensorBoard setup on Amazon EKS 
This document explains how to setup TensorBoard on [Amazon EKS](https://aws.amazon.com/eks/).

## Prerequisite
1. Create [EKS cluster using GPU](eks-gpu.md)
2. Setup [Kubeflow](kubeflow.md)

## Steps 

1. Manually create secret for aws credential. Please check [document](aws-credential-secret.md). Remember secret name and data fields.

2. Install tensorboard jsonnet package and generate yaml files.

   ```
   # Navigate to ksonnet application folder
   cd ${KUBEFLOW_SRC}/${KFAPP}/ks_app


   export TENSORBOARD_COMPONENT=tensorboard-mnist
   ks pkg install kubeflow/tensorboard
   ks generate tensorboard-aws ${TENSORBOARD_COMPONENT}

   # configure tensorboard log path
   ks param set ${TENSORBOARD_COMPONENT} defaultTbImage tensorflow/tensorflow:1.12.0
   ks param set ${TENSORBOARD_COMPONENT} logDir s3://eks-kubeflow-example/tensorflow_logs/mnist/

   # confirure region and bucket
   ks param set ${TENSORBOARD_COMPONENT} s3AwsRegion us-west-2
   ks param set ${TENSORBOARD_COMPONENT} s3Endpoint s3.us-west-2.amazonaws.com
   ks param set ${TENSORBOARD_COMPONENT} s3UseHttps true
   ks param set ${TENSORBOARD_COMPONENT} s3VerifySsl true

   # configure aws credential
   ks param set ${TENSORBOARD_COMPONENT} s3SecretName aws-s3-secret
   ks param set ${TENSORBOARD_COMPONENT} s3SecretAccesskeyidKeyName AWS_ACCESS_KEY_ID
   ks param set ${TENSORBOARD_COMPONENT} s3SecretSecretaccesskeyKeyName AWS_SECRET_ACCESS_KEY

   # create tensorboard deployment and service
   ks apply default -c ${TENSORBOARD_COMPONENT} 
   ```

3. It will create a deployment which runs the tensorboard on event files. A service is also being created so that user can access tensorboard via browser
   ```
   kubectl port-forward svc/${TENSORBOARD_COMPONENT} 9000:9000
   ```
   ![TensorBoard](images/tensorboard.png)