# KubeFlow on Amazon EKS

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

3. Ksonnet

   1. Install: `brew install ksonnet/tap/ks` or `brew upgrade ksonnet/tap/ks`

   2. Check version:
   
   ```
   $ ks version
   ksonnet version: 0.12.0
   jsonnet version: v0.11.2
   client-go version: kubernetes-1.10.4
   ```

3. Install kubeflow:

   ```
   export KUBEFLOW_VERSION=0.2.5
   curl https://raw.githubusercontent.com/kubeflow/kubeflow/v${KUBEFLOW_VERSION}/scripts/deploy.sh | bash
   cd kubeflow_ks_app/
   ks show default > /tmp/manifests.yaml
   kubectl apply -f /tmp/manifests.yaml
   ```

   The workaround is tracked at https://github.com/ksonnet/ksonnet/issues/853.

4. Get complete memory and CPU for the cluster:

   ```
   kubectl get nodes -o=jsonpath="{range .items[*]}{.metadata.name}{'\t'}{.status.allocatable.memory}{'\t'}{.status.allocatable.cpu}{'\n'}{end}"
   ```

   Shows something like:

   ```
   ip-192-168-101-177.us-west-2.compute.internal 251643680Ki 32
   ip-192-168-196-254.us-west-2.compute.internal 251643680Ki 32
   ```
