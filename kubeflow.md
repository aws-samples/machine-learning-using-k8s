# KubeFlow on Amazon EKS

- Create EKS cluster with GPU nodes: `eksctl create cluster eks-gpu --node-type=p3.8xlarge --timeout=40m`
- Ksonnet
  - Install: `brew install ksonnet/tap/ks` or `brew upgrade ksonnet/tap/ks`
  - Check version:
    ```
    $ ks version
    ksonnet version: 0.12.0
    jsonnet version: v0.11.2
    client-go version: kubernetes-1.10.4
    ```
- Install kubeflow
  ```
  export KUBEFLOW_VERSION=0.2.5
  curl https://raw.githubusercontent.com/kubeflow/kubeflow/v${KUBEFLOW_VERSION}/scripts/deploy.sh | bash
  cd kubeflow_ks_app/
  ks show default > /tmp/manifests.yaml
  kubectl apply -f /tmp/manifests.yaml
  ```
  The workaround is tracked at https://github.com/ksonnet/ksonnet/issues/853.


