# Distributed Training using TensorFlow and Horovod on Amazon EKS with Synthetic Data

This document explains how to perform distributed training on [Amazon EKS](https://aws.amazon.com/eks/) using TensorFlow and [Horovod](https://github.com/uber/horovod) with synthetic imagenet dataset.

## Pre-requisite

1. Create [EKS cluster using GPU with Kubeflow](../../eks-gpu.md)

## Install MPI Operator

1. Install mpi package

   ```
   cd  ${KUBEFLOW_SRC}/${KFAPP}/ks_app
   ks pkg install kubeflow/mpi-job
   ```

1. Install mpi operator

   ```
   export MPI_OPERATOR=mpi-operator
   ks generate mpi-operator ${MPI_OPERATOR}
   ks param set image mpioperator/mpi-operator:0.1.0
   ks apply default -c ${MPI_OPERATOR}
   ```

1. Verify Installation

   ```
   kubectl get crd

   NAME                                         CREATED AT
   ...
   mpijobs.kubeflow.org                         2019-02-12T22:12:32Z
   ...

   $ kubectl -n kubeflow get deployment ${MPI_OPERATOR}

   NAME           DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
   mpi-operator   1         1         1            1           1m
   ```

## Launch MPI Training Job

1. Generate job prototype:

   ```
   export JOB_NAME=tf-resnet50-horovod-job
   ks generate mpi-job-custom ${JOB_NAME}
   ```

1. You can leverage [AWS Deep Learning Containers](https://aws.amazon.com/machine-learning/containers/) to Build a Docker image for Horovod using Dockerfile from `training/distributed_training/Dockerfile`. You will need to login to access the repository of [AWS Deep Learning Containers](https://aws.amazon.com/machine-learning/containers/) by running the command `$(aws ecr get-login --no-include-email --region us-east-1 --registry-ids 763104351884)` and then build command `docker image build -t ${YOUR_DOCKER_HUB_ID}/eks-kubeflow-horovod:latest .`. Alternatively, you can use the image `mpioperator/tensorflow-benchmarks:latest` that already exists on Docker Hub.

   ```
   ks param set ${JOB_NAME} image "mpioperator/tensorflow-benchmarks:latest"
   ```

1. Define the number of workers (containers) and number of GPU available per container:

   ```
   ks param set ${JOB_NAME} replicas 2
   ks param set ${JOB_NAME} gpusPerReplica 4
   ```

1. Formulate the MPI command based on official document from [Horovod](https://github.com/uber/horovod)

    ```
    EXEC="mpirun,-mca,btl_tcp_if_exclude,lo,-mca,pml,ob1,-mca,btl,^openib,--bind-to,none,-map-by,slot,-x,LD_LIBRARY_PATH,-x,PATH,-x,NCCL_DEBUG=INFO,python,scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py,--data_format=NCHW,--batch_size=256,--model=resnet50,--optimizer=sgd,--variable_update=horovod,--data_name=imagenet,--use_fp16"

    ks param set ${JOB_NAME} command ${EXEC}
    ```

    If more than one GPU is used, then you may have to replace `NCCL_SOCKET_IFNAME=eth0` with `NCCL_SOCKET_IFNAME=^docker0`.

1. Verify your job configuration, it will look like [mpi-job-template.yaml](../../samples/imagenet/distributed_training/mpi-job-template.yaml)

    ```
    ks show default -c ${JOB_NAME}
    ```

1. Deploy the config to your cluster

    ```
    ks apply default -c ${JOB_NAME}
    ```

1. Check the pod status and dump logs

    ```
    POD_NAME=$(kubectl -n kubeflow get pods -l mpi_job_name=${JOB_NAME},mpi_role_type=launcher -o name)

    kubectl -n kubeflow logs -f ${POD_NAME}
    ```

    Here is a [sample output](logs/tensorflow-horovod-synthetic-log.txt).

1. To delete job in Kubernetes and remove job configuration in your application,

    ```
    ks delete default -c ${JOB_NAME}  # delete job in kubernetes
    ks component rm ${JOB_NAME}       # delete manifest in your ksonnet application
    ```
