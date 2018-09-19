# KubeFlow on Amazon EKS

This document explains how to setup KubeFlow on Amazon EKS cluster. Make sure to have a [GPU-enabled Amazon EKS cluster](eks-gpu.md) ready.

## Setup KubeFlow on Amazon EKS

1. Install Ksonnet:

   ```
   brew install ksonnet/tap/ks
   ```

   Or upgrade:

   ```
   brew upgrade ksonnet/tap/ks
   ```

   Check version:

   ```
   $ ks version
   ksonnet version: 0.12.0
   jsonnet version: v0.11.2
   client-go version: kubernetes-1.10.4
   ```

2. Install kubeflow:

   Ksonnet almost always requires a GitHub access token setup to work. Otherwise it will quickly run into API access limits. Generate one at https://github.com/settings/tokens and set environmental variable `GITHUB_TOKEN=<token>`.

   Now, install kubeflow:

   ```
   export KUBEFLOW_VERSION=0.2.5
   curl https://raw.githubusercontent.com/kubeflow/kubeflow/v${KUBEFLOW_VERSION}/scripts/deploy.sh | bash
   ```

   Sometimes the following workaround may be required:

   ```
   cd kubeflow_ks_app/
   ks show default > /tmp/manifests.yaml
   kubectl apply -f /tmp/manifests.yaml
   ```

   This is tracked at https://github.com/ksonnet/ksonnet/issues/853.

7. Verify kubeflow:

   ```
   kubectl get pods
   NAME                                        READY     STATUS    RESTARTS   AGE
   ambassador-59cb5ccd89-bgbpc                 2/2       Running   0          1d
   ambassador-59cb5ccd89-wkf76                 2/2       Running   0          1d
   ambassador-59cb5ccd89-wvdz9                 2/2       Running   0          1d
   centraldashboard-7d7744cccb-g6hcn           1/1       Running   0          1d
   spartakus-volunteer-8bf586df9-xdtqf         1/1       Running   0          1d
   tf-hub-0                                    1/1       Running   0          1d
   tf-job-dashboard-bfc9bc6bc-h5lql            1/1       Running   0          1d
   tf-job-operator-v1alpha2-756cf9cb97-rkdtv   1/1       Running   0          1d
   ```

Now, run a [TensorFlow](tensorflow.md) job.
