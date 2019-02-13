# Distributed Training using TensorFlow and Horovod on Amazon EKS with Synthetic Data

This document explains how to perform distributed training on [Amazon EKS](https://aws.amazon.com/eks/) using TensorFlow and [Horovod](https://github.com/uber/horovod) with synthetic imagenet dataset.

## Prerequisite

1. Create [EKS cluster using GPU](eks-gpu.md)
2. Install [Kubeflow](kubeflow.md)


## Install MPI Operator
1. Install mpi package

   ```
   ks pkg install kubeflow/mpi-job
   ```

2. Install mpi operator

   ```
   export MPI_OPERATOR=mpi-operator
   ks generate mpi-operator ${MPI_OPERATOR}
   ks apply default -c ${MPI_OPERATOR}
   ```
3. Verify Installation

   ```
   $ kubectl get crd
   NAME                                         CREATED AT
   ...
   mpijobs.kubeflow.org                         2019-02-12T22:12:32Z
   ...

   kubectl -n kubeflow get deployment ${MPI_OPERATOR}
   NAME           DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
   mpi-operator   1         1         1            1           1m

   ```

## Launch MPI Training Job

1. Generate job prototype
   ```
   export JOB_NAME=tf-resnet50-horovod-job
   ks generate mpi-job-custom ${JOB_NAME}

   ```

2. Build a Docker image for Horovod using Dockerfile from `training/distributed_training/Dockerfile` and the command `docker image build -t ${YOUR_DOCKER_HUB_ID}/eks-kubeflow-horovod:latest .`. Alternatively, you can use the image `mpioperator/tensorflow-benchmarks:latest` that already exists on Docker Hub.

   ```
   ks param set ${JOB_NAME} image "mpioperator/tensorflow-benchmarks:latest"
   ```

3. Define the number of workers (containers) and number of GPU available per container

   ```
   ks param set ${JOB_NAME} replicas 2
   ks param set ${JOB_NAME} gpusPerReplica 4
   ```

4. Formulate the MPI command based on official document from [Horovod](https://github.com/uber/horovod)

    ```
    EXEC="mpirun,-mca,btl_tcp_if_exclude,lo,-mca,pml,ob1,-mca,btl,^openib,--bind-to,none,-map-by,slot,-x,LD_LIBRARY_PATH,-x,PATH,-x,NCCL_DEBUG=INFO,python,scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py,--data_format=NCHW,--batch_size=256,--model=resnet50,--optimizer=sgd,--variable_update=horovod,--data_name=imagenet,--use_fp16"

    ks param set ${JOB_NAME} command ${EXEC}
    ```

    If more than one GPU is used, then you may have to replace `NCCL_SOCKET_IFNAME=eth0` with `NCCL_SOCKET_IFNAME=^docker0`.

5. Verify your job configuration, it will look like [mpi-job-template.yaml](training/distributed_training/mpi-job-template.yaml)

    ```
    ks show default -c ${JOB_NAME}
    ```

6. Deploy the config to your cluster

    ```
    ks apply default -c ${JOB_NAME}
    ```

7. Check the pod status and dump logs

    ```
    POD_NAME=$(kubectl -n kubeflow get pods -l mpi_job_name=${JOB_NAME},mpi_role_type=launcher -o name)

    kubectl -n kubeflow logs -f ${POD_NAME}
    ```

    Here is a [sample output](logs/tensorflow-horovod-synthetic-log.txt).

8. To delete job in kubernetes and remove job configuration in your application,

    ```
    ks delete default -c ${JOB_NAME}  # delete job in kubernetes
    ks component rm ${JOB_NAME}       # delete manifest in your ksonnet application
    ```
