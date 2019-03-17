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

   # absolute directy to download the source to
   export KUBEFLOW_SRC=/tmp/kubeflow_src

   # name for kubeflow deployment, ksonnet app will be created in ${KFAPP}/ks_app
   export KFAPP=eks-kubeflow

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
   NAME                                                      READY   STATUS    RESTARTS   AGE
   ambassador-5cf8cd97d5-chvzk                               1/1     Running   0          3m
   ambassador-5cf8cd97d5-fn9kg                               1/1     Running   0          3m
   ambassador-5cf8cd97d5-vpgjf                               1/1     Running   0          3m
   argo-ui-7c9c69d464-b8wtn                                  1/1     Running   0          2m
   centraldashboard-6f47d694bd-8cjpm                         1/1     Running   0          3m
   jupyter-0                                                 1/1     Running   0          3m
   katib-ui-6bdb7d76cc-jnm2l                                 1/1     Running   0          1m
   metacontroller-0                                          1/1     Running   0          2m
   minio-7bfcc6c7b9-tqzms                                    1/1     Running   0          2m
   ml-pipeline-6fdd759597-7pd7s                              1/1     Running   0          2m
   ml-pipeline-persistenceagent-5669f69cdd-pfmq8             1/1     Running   0          2m
   ml-pipeline-scheduledworkflow-9f6d5d5b6-bpmx5             1/1     Running   0          2m
   ml-pipeline-ui-67f79b964d-7v4g6                           1/1     Running   0          1m
   mysql-6f6b5f7b64-smw72                                    1/1     Running   0          2m
   pytorch-operator-6f87db67b7-fftct                         1/1     Running   0          2m
   spartakus-volunteer-567784fdd5-p2bkk                      1/1     Running   0          2m
   studyjob-controller-774d45f695-65hcn                      1/1     Running   0          1m
   tf-job-dashboard-5f986cf99d-fsd77                         1/1     Running   0          2m
   tf-job-operator-v1beta1-5876c48976-pxg54                  1/1     Running   0          2m
   vizier-core-fc7969897-crdtl                               1/1     Running   1          1m
   vizier-core-rest-6fcd4665d9-kkd87                         1/1     Running   0          1m
   vizier-db-777675b958-sbz2s                                1/1     Running   0          1m
   vizier-suggestion-bayesianoptimization-54db8d594f-7tm92   1/1     Running   0          1m
   vizier-suggestion-grid-6f5d9d647f-fkqp4                   1/1     Running   0          1m
   vizier-suggestion-hyperband-59dd9bb9bc-zf8h2              1/1     Running   0          1m
   vizier-suggestion-random-6dd597c997-bmvwg                 1/1     Running   0          1m
   workflow-controller-5c95f95f58-v8w4q                      1/1     Running   0          2m
   ```
   > You may not need all the componets. If you want to customize components, please check [Kubeflow Customization](kubeflow-custom.md).

5. Once done playing, uninstall Kubeflow:

   ```
   cd ${KUBEFLOW_SRC}/${KFAPP}
   ${KUBEFLOW_SRC}/scripts/kfctl.sh delete k8s
   ```