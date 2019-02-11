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
   ksonnet version: 0.13.1
   jsonnet version: v0.11.2
   client-go version: kubernetes-1.10.4
   ```

2. Install kubeflow:

   Ksonnet almost always requires a GitHub access token setup to work. Otherwise it will quickly run into API access limits. Generate one at https://github.com/settings/tokens and set environmental variable:

   ```
   export GITHUB_TOKEN=<token>
   ```

   Now, install kubeflow:

   ```
   # master is nightly version, you can also choose reliable version here https://github.com/kubeflow/kubeflow/releases
   export KUBEFLOW_TAG=v0.4.1
   export KUBEFLOW_SRC=/tmp/kubeflow_src # absolute directy to download the source to
   export KFAPP=eks-kubeflow # name for kubeflow deployment, ksonnet app will be created in ${KFAPP}/ks_app

   mkdir ${KUBEFLOW_SRC} && cd ${KUBEFLOW_SRC}
   curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash

   ${KUBEFLOW_SRC}/scripts/kfctl.sh init ${KFAPP} --platform none
   cd ${KFAPP}
   ${KUBEFLOW_SRC}/scripts/kfctl.sh generate k8s
   ${KUBEFLOW_SRC}/scripts/kfctl.sh apply k8s
   ```

   Sometimes the following workaround may be required to debug kubernetes resource files:

   ```
   cd ${KUBEFLOW_SRC}/${KFAPP}/ks_app
   ks show default > /tmp/manifests.yaml
   kubectl apply -f /tmp/manifests.yaml
   ```

   This is tracked at https://github.com/ksonnet/ksonnet/issues/853.

4. Verify kubeflow:

   ```
   kubectl get pods -n kubeflow
   NAME                                                      READY   STATUS    RESTARTS   AGE
   ambassador-5cf8cd97d5-25lgp                               1/1     Running   0          2m
   ambassador-5cf8cd97d5-9xgmz                               1/1     Running   0          2m
   ambassador-5cf8cd97d5-hqqnv                               1/1     Running   0          2m
   argo-ui-7c9c69d464-mjsj7                                  1/1     Running   0          2m
   centraldashboard-6f47d694bd-cn46v                         1/1     Running   0          2m
   jupyter-0                                                 1/1     Running   0          2m
   katib-ui-6bdb7d76cc-hxlbc                                 1/1     Running   0          1m
   metacontroller-0                                          1/1     Running   0          2m
   minio-7bfcc6c7b9-qdmhg                                    1/1     Running   0          2m
   ml-pipeline-6fdd759597-2zllr                              1/1     Running   0          2m
   ml-pipeline-persistenceagent-5669f69cdd-8dhms             1/1     Running   0          2m
   ml-pipeline-scheduledworkflow-9f6d5d5b6-hzhhp             1/1     Running   0          2m
   ml-pipeline-ui-67f79b964d-b84lt                           1/1     Running   0          2m
   mysql-6f6b5f7b64-8cz6k                                    1/1     Running   0          2m
   pytorch-operator-6f87db67b7-mnnwt                         1/1     Running   0          2m
   spartakus-volunteer-847cc98fd4-zlch9                      1/1     Running   0          2m
   studyjob-controller-774d45f695-zx8xn                      1/1     Running   0          1m
   tf-job-dashboard-5f986cf99d-snnnf                         1/1     Running   0          2m
   tf-job-operator-v1beta1-5876c48976-jqnz5                  1/1     Running   0          2m
   ...
   ```
   > You may not need all the componets. If you want to customize components, please check [Kubeflow Customization](kubeflow-custom.md).

5. Uninstall Kubeflow:

   ```
   cd ${KUBEFLOW_SRC}/${KFAPP}
   ${KUBEFLOW_SRC}/scripts/kfctl.sh delete k8s
   ```