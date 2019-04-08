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
   kubectl get pods -n=kubeflow
   NAME                                                      READY   STATUS    RESTARTS   AGE
   ambassador-5cf8cd97d5-68xgv                               1/1     Running   0          19m
   ambassador-5cf8cd97d5-cxp85                               1/1     Running   0          19m
   ambassador-5cf8cd97d5-r57hc                               1/1     Running   0          19m
   argo-ui-7c9c69d464-p7mjh                                  1/1     Running   0          17m
   centraldashboard-6f47d694bd-qd56p                         1/1     Running   0          18m
   jupyter-0                                                 1/1     Running   0          18m
   katib-ui-6bdb7d76cc-z9dv5                                 1/1     Running   0          16m
   metacontroller-0                                          1/1     Running   0          17m
   minio-7bfcc6c7b9-d8xqf                                    1/1     Running   0          17m
   ml-pipeline-6fdd759597-n9zws                              1/1     Running   0          17m
   ml-pipeline-persistenceagent-5669f69cdd-gdzwq             1/1     Running   1          16m
   ml-pipeline-scheduledworkflow-9f6d5d5b6-zfqtd             1/1     Running   0          16m
   ml-pipeline-ui-67f79b964d-jrwx6                           1/1     Running   0          16m
   mysql-6f6b5f7b64-bg2vp                                    1/1     Running   0          17m
   pytorch-operator-6f87db67b7-4bksz                         1/1     Running   0          17m
   spartakus-volunteer-6f5f47f95-cl5sf                       1/1     Running   0          17m
   studyjob-controller-774d45f695-2k6t8                      1/1     Running   0          16m
   tf-job-dashboard-5f986cf99d-nqxm7                         1/1     Running   0          18m
   tf-job-operator-v1beta1-5876c48976-zbmrq                  1/1     Running   0          18m
   vizier-core-fc7969897-rns98                               1/1     Running   1          16m
   vizier-core-rest-6fcd4665d9-bf69g                         1/1     Running   0          16m
   vizier-db-777675b958-kt8p2                                1/1     Running   0          16m
   vizier-suggestion-bayesianoptimization-54db8d594f-5srk6   1/1     Running   0          16m
   vizier-suggestion-grid-6f5d9d647f-tzgqw                   1/1     Running   0          16m
   vizier-suggestion-hyperband-59dd9bb9bc-mldbl              1/1     Running   0          16m
   vizier-suggestion-random-6dd597c997-8qdnr                 1/1     Running   0          16m
   workflow-controller-5c95f95f58-nvg9l                      1/1     Running   0          17m
   ```
   
   You may not need all the componets. If you want to customize components, please check [Kubeflow Customization](kubeflow-custom.md).

5. Once done playing, uninstall KubeFlow:

   ```
   cd ${KUBEFLOW_SRC}/${KFAPP}
   ${KUBEFLOW_SRC}/scripts/kfctl.sh delete k8s
   ```