# Distributed Training using TensorFlow and Horovod on Amazon EKS with Synthetic Data

This document explains how to perform distributed training on [Amazon EKS](https://aws.amazon.com/eks/) using TensorFlow and [Horovod](https://github.com/uber/horovod) with synthetic dataset. 

## Prerequisite

1. Create [EKS cluster using GPU](eks-gpu.md)

1. Install [Kubeflow](kubeflow.md)

## Steps

1. Create namespace:

    ```
    NAMESPACE=kubeflow-dist-train; kubectl create namespace ${NAMESPACE}
    ```

1. Create ksonnet app:

    ```
    APP_NAME=kubeflow-tf-hvd; ks init ${APP_NAME}; cd ${APP_NAME}
    ```

1. Set as default namespace:

    ```
    ks env set default --namespace ${NAMESPACE}
    ```

1. Create secret for ssh access between nodes

    ```
    SECRET=openmpi-secret; mkdir -p .tmp; yes | ssh-keygen -N "" -f .tmp/id_rsa
    kubectl delete secret ${SECRET} -n ${NAMESPACE} || true
    kubectl create secret generic ${SECRET} -n ${NAMESPACE} --from-file=id_rsa=.tmp/id_rsa --from-file=id_rsa.pub=.tmp/id_rsa.pub --from-file=authorized_keys=.tmp/id_rsa.pub
    ```

1. Install Kubeflow openmpi component

    ``` 
    VERSION=master
    ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${VERSION}/kubeflow
    ks pkg install kubeflow/openmpi@${VERSION}
    ```

1. Build a Docker image for Horovod using Dockerfile from `training/distributed_training/Dockerfile` and the command `docker image build -t arungupta/horovod .`. Alternatively, you can use the image that already exists on Docker Hub:

    ```
    IMAGE=rgaut/horovod:latest
    IMAGE=armandmcqueen/horovod_benchmark:v1
    ```

1. Define the number of workers (number of machines) and number of GPU available per machine

    ```
    WORKERS=2; GPU=4
    ```

1. Formulate the MPI command based on official document from [Horovod](https://github.com/uber/horovod)

    ```
    EXEC="mpiexec -np 8 --hostfile /kubeflow/openmpi/assets/hostfile --allow-run-as-root --display-map --tag-output --timestamp-output -mca btl_tcp_if_exclude lo,docker0 --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 -mca btl ^openib sh -c 'NCCL_SOCKET_IFNAME=eth0 NCCL_MIN_NRINGS=8 NCCL_DEBUG=INFO python3.6 /examples/official-benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py --num_batches=100 --model vgg16 --batch_size 64 --variable_update horovod --horovod_device gpu --use_fp16'"
    ```

    If more than one GPU is used, then you may have to replace `NCCL_SOCKET_IFNAME=eth0` with `NCCL_SOCKET_IFNAME=^docker0`.

   MPI command needs some explanations. `-np` represents a total number process which will be equal to `WORKERS` * `GPU`.

1. Generate the config

    ```
    COMPONENT=openmpi
    ks generate openmpi ${COMPONENT} --image ${IMAGE} --secret ${SECRET} --workers ${WORKERS} --gpu ${GPU} --exec "${EXEC}"
    ```

1. Deploy the config to your cluster

    ```
    ks apply default
    ```

1. Check the pod status

    ```
    kubectl get pod -n ${NAMESPACE} -o wide
    ```

1. Save the log

    ```
    mkdir -p results
    kubectl logs -n ${NAMESPACE} -f ${COMPONENT}-master > results/benchmark_1.out
    ```

    Here is a [sample output](tensorflow-horovod-log.txt).

1. To iterate quickly. Remove pods, recreate openmpi component, restart from generate openmpi command

    ```
    ks delete default
    ks component rm openmpi 
    ```

1. [Optional] EXEC command for 4 workers 8 GPU

    ```
    WORKERS=4
    GPU=8
    EXEC="mpiexec -np 32 --hostfile /kubeflow/openmpi/assets/hostfile --allow-run-as-root --display-map --tag-output --timestamp-output -mca btl_tcp_if_exclude lo,docker0 --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 -mca btl ^openib sh -c 'NCCL_SOCKET_IFNAME=eth0 NCCL_MIN_NRINGS=8 NCCL_DEBUG=INFO python3.6 /examples/official-benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py --num_batches=100 --model vgg16 --batch_size 64 --variable_update horovod --horovod_device gpu --use_fp16'"
    ```

    Then follow the steps from 10-13.
