# Store AWS Credential as Kubernetes Secret
Users may store machine learning trained model and training events on S3. In order for service like Tensorboard, Tensorflow Serving to get access to files on S3, aws credential is required. Kubernetes secret is intended to hold sensitive informatio, such as aws credentials.

## Steps

1. You can check your credentails
   ```
   $ cat ~/.aws/credentials
   [default]
   aws_access_key_id = FAKEAWSACCESSKEYID
   aws_secret_access_key = FAKEAWSSECRETACCESSKEY
   ```
2. Manually encode credentials using base 64.

   ```
   $ echo -n 'FAKEAWSACCESSKEYID' | base64
   RkFLRUFXU0FDQ0VTU0tFWUlE

   $ echo -n 'FAKEAWSSECRETACCESSKEY' | base64
   RkFLRUFXU1NFQ1JFVEFDQ0VTU0tFWQ==
   ```

3. Create a secret yaml file.

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

4. Apply to kubernetes. `kubectl -n kubeflow apply secret.yaml`