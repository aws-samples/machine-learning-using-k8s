# KubeFlow on Amazon EKS

This document explains how to setup KubeFlow on Amazon EKS cluster. Then it will explain how to run a TensorFlow model using KubeFlow on this cluster.

## Setup KubeFlow on Amazon EKS

1. Create EKS cluster with GPU nodes:

   ```
   eksctl create cluster eks-gpu --node-type=p3.8xlarge --timeout=40m
   ```
   
2. Apply NVIDIA driver:

   ```
   kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.10/nvidia-device-plugin.yml
   ```

   Check to the ensure GPUs are assigned:

   ```
   kubectl get nodes     "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
   NAME                                            GPU
   ip-192-168-101-177.us-west-2.compute.internal   4
   ip-192-168-196-254.us-west-2.compute.internal   4
   ```

   This will be simplified after https://github.com/weaveworks/eksctl/issues/205 is fixed.

3. Get memory, CPU and GPU for each node in the cluster:

   ```
   kubectl get nodes "-o=custom-columns=NAME:.metadata.name,MEMORY:.status.allocatable.memory,CPU:.status.allocatable.cpu,GPU:.status.allocatable.nvidia\.com/gpu"
   ```

   Shows something like:

   ```
   NAME                                            MEMORY        CPU       GPU
   ip-192-168-101-177.us-west-2.compute.internal   251643680Ki   32        4
   ip-192-168-196-254.us-west-2.compute.internal   251643680Ki   32        4
   ```

   The maximum number of GPUs that may be scheduled to a pod is capped by the number of GPUs available per node. By default, pods are scheduled on CPU. 

5. Install Ksonnet:

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

6. Install kubeflow:

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