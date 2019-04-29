# Distributed Training using TensorFlow and Horovod on Amazon EKS with ImageNet Data

This document explains how to perform distributed training on [Amazon EKS](https://aws.amazon.com/eks/) using TensorFlow and [Horovod](https://github.com/uber/horovod) with [ImageNet dataset](http://www.image-net.org/). The following steps can be ued for any data set though.

## Pre-requisite

1. Create [EKS cluster using GPU with Kubeflow](../../eks-gpu.md).

1. Create an [EFS](https://aws.amazon.com/efs/) and mount it to any worker node as explained in [Setup EFS on EKS](../../efs-on-eks-worker-nodes.md).

1. Download and put prepare ImageNet dataset on EFS path `/imagenet`. Please check [tutorial](#download-and-preprocess-imagenet-data)

## Steps

1. Follow [steps](tensorflow-horovod-synthetic.md#install-mpi-operator) to install mpi-operator

1. Prepare Persistent Volumne (PV) and Persistent Volume Claim (PVC)

   - Create the Persistent Volume (PV) based on EFS. You need to update the name of EFS server in the Kubernetes manifest file. Storage capacity based on dataset size and other requirements can be updated as well.

      ```
      kubectl create -f samples/imagenet/distributed_training/dist_pv.yaml
      ```

    - Create the Persistent Volume Claim (PVC) based on EFS. The storage capacity based on PV's capacity may adjusted in the manifest. The storage capacity of PVC should be the at most storage capacity of PV.

      ```
      kubectl create -f samples/imagenet/distributed_training/dist_pvc.yaml
      ```

    - Make sure that PV has been claimed by PVC under same namespace:

      ```
      kubectl get pv -n kubeflow

      NAME       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                              STORAGECLASS   REASON   AGE
      nfs-data   85Gi       RWX            Retain           Bound    kubeflow/nfs-external   nfs-external            58s
      ```

1. Prepare training job. Check [here](tensorflow-horovod-synthetic.md#launch-mpi-training-job) for more details

   ```
   export JOB_NAME=tf-resnet50-horovod-job
   ks generate mpi-job-custom ${JOB_NAME}

   ks param set ${JOB_NAME} image "mpioperator/tensorflow-benchmarks:latest"
   ks param set ${JOB_NAME} replicas 2
   ks param set ${JOB_NAME} gpusPerReplica 4

   EXEC="mpirun,-mca,btl_tcp_if_exclude,lo,-mca,pml,ob1,-mca,btl,^openib,--bind-to,none,-map-by,slot,-x,LD_LIBRARY_PATH,-x,PATH,-x,NCCL_DEBUG=INFO,python,scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py,--data_format=NCHW,--batch_size=256,--model=resnet50,--optimizer=sgd,--variable_update=horovod,--data_name=imagenet,--use_fp16,--nodistortions,--gradient_repacking=8,--data_dir=/data/imagenet"
   ```
   > Note: Instead of using synthetic data, job will read from `--data_dir`.

1. Right now, `mpi-job-custom` doesn't support volume in jsonnet, we can manually mount volumes.

   ```
   ks show default -c ${JOB_NAME} > /tmp/training_job.yaml
   vim  /tmp/training_job.yaml # add volumes
   ```
   Please check [template](../../samples/imagenet/distributed_training/mpi-job-template-nfs.yaml)

1. Deploy training job
   ```
   ks apply default -c ${JOB_NAME}
   ```

1. Check pod status and logs
    ```
    POD_NAME=$(kubectl -n kubeflow get pods -l mpi_job_name=${JOB_NAME},mpi_role_type=launcher -o name)

    kubectl -n kubeflow logs -f ${POD_NAME}
    ```

    Here is a [sample output](logs/tensorflow-horovod-imagenet-log.txt).

## Appendix

### Download and Pre-process ImageNet Data

If you work for Amazon, then reach out to the authors of this document to have access to the data. Otherwise, follow the instructions below.

1. Download [ImageNet](http://image-net.org/download-images) dataset to EFS in the `data` directory. This would typically be in the directory `/home/ec2-user/efs/data`. Use `Download Original Images (for non-commercial research/educational use only)` option.

2. TensorFlow consumes the ImageNet data in a specific format. You can preprocess them by downloading and modifying the script:

    ```
    curl -O https://raw.githubusercontent.com/aws-samples/deep-learning-models/master/utils/tensorflow/preprocess_imagenet.sh
    chmod +x preprocess_imagenet.sh
    ```

    The following values need to be changed:

    * `[your imagenet account]`
    * `[your imagenet access key]`
    * `[PATH TO TFRECORD TRAINING DATASET]`
    * `[PATH TO RESIZED TFRECORD TRAINING DATASET]`
    * `[PATH TO TFRECORD VALIDATION DATASET]`
    * `[PATH TO RESIZED TFRECORD VALIDATION DATASET]`

    Execute the script:

    ```
    ./preprocess_imagenet.sh
    ```
