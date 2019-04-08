# Store AWS Credentials in Kubernetes Secret

Users may store machine learning trained model and training events on S3. 

[TensorBoard](https://github.com/tensorflow/tensorboard) is a suite of web applications for inspecting and understanding your TensorFlow runs and graphs. [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving) is a flexible, high-performance serving system for machine learning models, designed for production environments. These models are stores on S2. In order for TensorBoard and TensorFlow Serving to get access to files on S3, AWS credentials are required. These credentials are stored in Kubernetes secrets.

1. Check your AWS credentials:

   ```
   $ cat ~/.aws/credentials

   [default]
   aws_access_key_id = FAKEAWSACCESSKEYID
   aws_secret_access_key = FAKEAWSSECRETACCESSKEY
   ```

2. Manually encode credentials using base 64:

   ```
   $ echo -n 'FAKEAWSACCESSKEYID' | base64
   RkFLRUFXU0FDQ0VTU0tFWUlE

   $ echo -n 'FAKEAWSSECRETACCESSKEY' | base64
   RkFLRUFXU1NFQ1JFVEFDQ0VTU0tFWQ==
   ```

3. Create a secret yaml file:

   ```
   apiVersion: v1
   kind: Secret
   metadata:
     name: aws-s3-secret
   type: Opaque
   data:
     AWS_ACCESS_KEY_ID: RkFLRUFXU0FDQ0VTU0tFWUlE
     AWS_SECRET_ACCESS_KEY: RkFLRUFXU1NFQ1JFVEFDQ0VTU0tFWQ==
   ```

4. Apply to EKS cluster:

   ```
   kubectl -n kubeflow apply -f secret.yaml
   ```
