# Distributed Training using TensorFlow and Horovod on Amazon EKS with ImageNet Data

This document explains how to perform distributed training on [Amazon EKS](https://aws.amazon.com/eks/) using TensorFlow and [Horovod](https://github.com/uber/horovod) with [ImageNet dataset](http://www.image-net.org/). The following steps can be ued for any data set though.

## Prerequisite

1. Create [EKS cluster using GPU](eks-gpu.md).

1. Install [Kubeflow](kubeflow.md).

1. Create an [EFS](https://aws.amazon.com/efs/) and mount it to each worker nodes as explained in [efs-on-eks-worker-nodes.md](efs-on-eks-worker-nodes.md).

### ImageNet Data

If you work for Amazon, then reach out to the authors of this document to have access to the data. Otherwise, follow the instructions below.

1. Download [ImageNet](http://image-net.org/download-images) dataset to EFS in the `data` directory. This would typically be in the directory `/home/ec2-user/efs/data`. Use `Download Original Images (for non-commercial research/educational use only)` option.

1. TensorFlow consumes the ImageNet data in a specific format. You can preprocess them by downloading and modifying the script:

    ```
    curl -O https://raw.githubusercontent.com/aws-samples/deep-learning-models/master/utils/tensorflow/preprocess_imagenet.sh
    chmod +x preprocess_imagenet.sh
    ```

    The following values need to be changed:

    1. `[your imagenet account]`
    1. `[your imagenet access key]`
    1. `[PATH TO TFRECORD TRAINING DATASET]`
    1. `[PATH TO RESIZED TFRECORD TRAINING DATASET]`
    1. `[PATH TO TFRECORD VALIDATION DATASET]`
    1. `[PATH TO RESIZED TFRECORD VALIDATION DATASET]`

    Execute the script:

    ```
    ./preprocess_imagenet.sh
    ```

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

1. Create the Persistent Volume (PV) based on EFS. You need to update the name of EFS server in the Kubernetes manifest file. Storage capacity based on dataset size and other requirements can be updated as well.

    ```
    kubectl create -f ../training/distributed_training/dist_pv.yaml
    ```

1. Create the Persistent Volume Claim (PVC) based on EFS. The storage capacity based on PV's capacity may adjusted in the manifest. The storage capacity of PVC should be the at most storage capacity of PV.

    ```
    kubectl create -f ../training/distributed_training/dist_pvc.yaml
    ```

1. Make sure that PV has been claimed by PVC under same namespace. You can verify that by running the command:

    ```
    kubectl get pv -n ${NAMESPACE}
    NAME       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                              STORAGECLASS   REASON   AGE
nfs-data   85Gi       RWX            Retain           Bound    kubeflow-dist-train/nfs-external   nfs-external            58s
    ```

1. Create secret for ssh access between nodes:

    ```
    SECRET=openmpi-secret; mkdir -p .tmp; yes | ssh-keygen -N "" -f .tmp/id_rsa
    kubectl delete secret ${SECRET} -n ${NAMESPACE} || true
    kubectl create secret generic ${SECRET} -n ${NAMESPACE} --from-file=id_rsa=.tmp/id_rsa --from-file=id_rsa.pub=.tmp/id_rsa.pub --from-file=authorized_keys=.tmp/id_rsa.pub
    ```

1. Install Kubeflow openmpi component:

    ``` 
    VERSION=master
    ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${VERSION}/kubeflow
    ks pkg install kubeflow/openmpi@${VERSION}
    ```

1. Build a Docker image for Horovod using Dockerfile from `training/distributed_training/Dockerfile` and the command `docker image build -t arungupta/horovod .`. Alternatively, you can use the image that already exists on Docker Hub:

    ```
    IMAGE=rgaut/horovod:latest
    ```

1. Define the number of workers (number of machines) and number of GPU available per machine:

    ```
    WORKERS=2; GPU=4
    ```

1. Formulate the MPI command based on official document from [Horovod](https://github.com/uber/horovod):

    ```
    EXEC="mpiexec -np 8 --hostfile /kubeflow/openmpi/assets/hostfile --allow-run-as-root --display-map --tag-output --timestamp-output -mca btl_tcp_if_exclude lo,docker0 --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 -mca btl ^openib sh -c 'NCCL_SOCKET_IFNAME=eth0 NCCL_MIN_NRINGS=8 NCCL_DEBUG=INFO python3.6 /examples/official-benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py --num_batches=100 --model vgg16 --batch_size 64  --data_name=imagenet  --data_dir=/mnt/data --variable_update horovod --horovod_device gpu --use_fp16'"
    ```

    If more than one GPU is used, then you may have to replace `NCCL_SOCKET_IFNAME=eth0` with `NCCL_SOCKET_IFNAME=^docker0`.

    MPI command needs some explanations. `-np` represents a total number process which will be equal to `WORKERS` * `GPU`.

1. Generate the config:

    ```
    COMPONENT=openmpi
    ks generate openmpi ${COMPONENT} --image ${IMAGE} --secret ${SECRET} --workers ${WORKERS} --gpu ${GPU} --exec "${EXEC}"
    ```

1. Set the parameter for the created volume:

    ```
    ks param set ${COMPONENT} volumes '[{ "name": "efs-pvc", "persistentVolumeClaim": { "claimName": "nfs-external" }}]'
    ```

1. Set the parameter for volumeMounts:

    ```
    ks param set ${COMPONENT} volumeMounts '[{ "name": "efs-pvc", "mountPath": "/mnt"}]'
    ```

    This command will make the `data` available under `/mnt/data` directory for each pod.

1. Deploy the config to your cluster:

    ```
    ks apply default
    ```

1. Check the pod status:

    ```
    kubectl get pod -n ${NAMESPACE} -o wide
    ```

1. Save the log:

    ```
    mkdir -p results
    kubectl logs -n ${NAMESPACE} -f ${COMPONENT}-master > results/benchmark_1.out
    ```

    Here is a [sample output](tensorflow-horovod-imagenet-log.txt).

1. To iterate quickly. Remove pods, recreate openmpi component, restart from generate openmpi command

    ```
    ks delete default
    ks component rm openmpi 
    ```

1. [Optional] EXEC command for 4 workers 8 GPU

    ```
    WORKERS=4
    GPU=8
    EXEC="mpiexec -np 32 --hostfile /kubeflow/openmpi/assets/hostfile --allow-run-as-root --display-map --tag-output --timestamp-output -mca btl_tcp_if_exclude lo,docker0 --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 -mca btl ^openib sh -c 'NCCL_SOCKET_IFNAME=eth0 NCCL_MIN_NRINGS=8 NCCL_DEBUG=INFO python3.6 /examples/official-benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py --num_batches=100 --model vgg16 --batch_size 64  --data_name=imagenet  --data_dir=/mnt/data --variable_update horovod --horovod_device gpu --use_fp16'"
    ```

    Then follow the steps from 10-13.
