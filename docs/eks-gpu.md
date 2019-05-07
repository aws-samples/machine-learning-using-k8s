# Create Amazon EKS cluster with GPU-enabled workers and Kubeflow

This document explains how to create an Amazon EKS cluster with GPU-enabled workers.

This documentation is from official [Kubeflow on AWS](https://www.kubeflow.org/docs/aws/customizing-aws/) documentation. Please check website for more details for Kubeflow on AWS.
If you meet any problem during installation, please check [Troubleshooting Deployments on Amazon EKS](https://www.kubeflow.org/docs/aws/troubleshooting-aws/)

## Prerequisites
* Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)
* Install and configure the AWS Command Line Interface (AWS CLI):
    * Install the [AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
    * Configure the AWS CLI by running the following command: `aws configure`.
    * Enter your Access Keys ([Access Key ID and Secret Access Key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)).
    * Enter your preferred AWS Region and default output options.
* Install [eksctl](https://github.com/weaveworks/eksctl) (version 0.1.27 or newer).
* Install [jq](https://stedolan.github.io/jq/download/).
* Install [ksonnet](https://github.com/ksonnet/ksonnet). (`brew install ksonnet/tap/ks` for mac user)


## Create cluster and install Kubeflow

1. Subscribe to the GPU supported AMI:

   https://aws.amazon.com/marketplace/pp/B07GRHFXGM

1. Run the following commands to download the latest `kfctl.sh`:

   ```
   export KUBEFLOW_SRC=/tmp/kubeflow-aws
   export KUBEFLOW_TAG=master

   mkdir -p ${KUBEFLOW_SRC} && cd ${KUBEFLOW_SRC}
   curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
   ```

   * `/tmp/kubeflow-aws` is full path to your preferred download directory.

1. Run the following commands to set up your environment and initialize the cluster.

   ```
   export KFAPP=kfapp
   export REGION=us-west-2
   export AWS_CLUSTER_NAME=kubeflow-aws

   ${KUBEFLOW_SRC}/scripts/kfctl.sh init ${KFAPP} --platform aws \
   --awsClusterName ${AWS_CLUSTER_NAME} \
   --awsRegion ${REGION}
   ```

   * `AWS_CLUSTER_NAME` - A unique name for your Amazon EKS cluster.
   * `KFAPP` - Use a relative directory name here rather than absolute path, such as `kfapp`.
   * `REGION` - Use the AWS Region you want to create your cluster in.

1. Generate and apply platform changes.

   You can customize your cluster configuration, control plane logging, and private cluster endpoint access before you `apply platform`, please see [Customizing Kubeflow on AWS](https://www.kubeflow.org/docs/aws/customizing-aws/) for more information.

   ```shell
   cd ${KFAPP}
   ${KUBEFLOW_SRC}/scripts/kfctl.sh generate platform
   # Customize your Amazon EKS cluster configuration before following the next step
   ```

1. Open `cluster_config.yaml` and update the file so that it looks like as shown:

   ```
   apiVersion: eksctl.io/v1alpha5
   kind: ClusterConfig
   metadata:
     # AWS_CLUSTER_NAME and AWS_REGION will override `name` and `region` here.
     name: kubeflow-aws
     region: us-west-2
     version: '1.12'
   # If your region has multiple availability zones, you can specify 3 of them.
   #availabilityZones: ["us-west-2b", "us-west-2c", "us-west-2d"]

   # NodeGroup holds all configuration attributes that are specific to a nodegroup
   # You can have several node group in your cluster.
   nodeGroups:
     #- name: cpu-nodegroup
     #  instanceType: m5.2xlarge
     #  desiredCapacity: 1
     #  minSize: 0
     #  maxSize: 2
     #  volumeSize: 30

     # Example of GPU node group
     - name: Tesla-V100
       instanceType: p3.8xlarge
       availabilityZones: ["us-west-2b"]
       desiredCapacity: 2
       minSize: 0
       maxSize: 2
       volumeSize: 50
       ssh:
         allow: true
         publicKeyPath: '~/.ssh/id_rsa.pub'
   ```

   Then apply the changes:

   ```shell
   # vim ${KUBEFLOW_SRC}/${KFAPP}/aws_config/cluster_config.yaml
   ${KUBEFLOW_SRC}/scripts/kfctl.sh apply platform
   ```

1. Generate and apply the Kubernetes changes.

   ```shell
   ${KUBEFLOW_SRC}/scripts/kfctl.sh generate k8s
   ```

   __*Important!!!*__ By default, these scripts create an AWS Application Load Balancer for Kubeflow that is open to public. This is good for development testing and for short term use, but we do not recommend that you use this configuration for production workloads.

   To secure your installation, you have two options:

   * Disable ingress before you `apply k8s`. Open `${KUBEFLOW_SRC}/${KFAPP}/env.sh` and edit the `KUBEFLOW_COMPONENTS` environment variable. Delete `,\"alb-ingress-controller\",\"istio-ingress\"` and save the file.

   * Follow the [instructions](https://www.kubeflow.org/docs/aws/authentication/) to add authentication before you `apply k8s`

   Once your customization is done or if you're fine to have a public endpoint for testing, you can run this command to deploy Kubeflow.
   ```shell
   ${KUBEFLOW_SRC}/scripts/kfctl.sh apply k8s
   ```

   This will take a few minutes for all pods get ready.

1. Get memory, CPU and GPU for each node in the cluster:

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

1. Verify kubeflow:

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

1. Once done playing, uninstall KubeFlow and cluster.

   ```
   cd ${KUBEFLOW_SRC}/${KFAPP}
   ${KUBEFLOW_SRC}/scripts/kfctl.sh delete all
   ```