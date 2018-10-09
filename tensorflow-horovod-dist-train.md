# Distributed training using TensorFlow and Horovod on Amazon EKS 

This document explains how to perform distributed training on [Amazon EKS](https://aws.amazon.com/eks/) using TensorFlow and Horovod with synthetic dataset. 

##Prerequisite
  A. EKS setup with worker nodes
  B. Install ksonnet Quick  
     ```
     brew install ksonnet/tap/ks
     ```
  C. Get a github token

## Steps
  1. Export Github Tokeb 
     ```
     export GITHUB_TOKEN=<your github token>
     ```

  2. Create namespace
     ```
     NAMESPACE=kubeflow-dist-train
     kubectl create namespace ${NAMESPACE}
     ```

  3. Create ksonnet app
     ```
     APP_NAME=kubeflow-tf-hvd
     ks init ${APP_NAME}
     cd ${APP_NAME}
     ```

  4. Set as default namespace
     ```
     ks env set default --namespace ${NAMESPACE}
     ```
  
  5. Create secret for ssh access between nodes
     ```
     SECRET=openmpi-secret
     mkdir -p .tmp
     yes | ssh-keygen -N "" -f .tmp/id_rsa
     kubectl delete secret ${SECRET} -n ${NAMESPACE} || true
     kubectl create secret generic ${SECRET} -n ${NAMESPACE} --from-file=id_rsa=.tmp/id_rsa --from-file=id_rsa.pub=.tmp/id_rsa.pub --from-file=authorized_keys=.tmp/id_rsa.pub
     ```
   
  6. Install Kubeflow openmpi component
     ``` 
     VERSION=master
     ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${VERSION}/kubeflow
     ks pkg install kubeflow/openmpi@${VERSION}
     ```

  7. Define Docker Image, you can build a docker image from `training/distributed_training/Dockerfile` or you can pull the already built image 
     ```
     IMAGE=rgaut/horovod:latest
     ```

  8. Define the number of workers (number of machines) and number of GPU available per machine. 
     ```
     WORKERS=3 
     GPU=1
     ```

  9. Formulate the MPI command based on official document from [Horovod](https://github.com/uber/horovod)
    
     ```
     EXEC="mpiexec -np 3 --hostfile /kubeflow/openmpi/assets/hostfile --allow-run-as-root --display-map --tag-output --timestamp-output -mca btl_tcp_if_exclude lo,docker0 --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 -mca btl ^openib sh -c 'NCCL_MIN_NRINGS=8 NCCL_DEBUG=INFO python3.6 /examples/official-benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py --num_batches=100 --model vgg16 --batch_size 64 --variable_update horovod --horovod_device gpu --use_fp16'"
     ```

     MPI command needs some explanations
     `-np` represents number of total process which will be equal to WORKERS*GPU

 10. Generate the config
     ```
     ks generate openmpi ${COMPONENT} --image ${IMAGE} --secret ${SECRET} --workers ${WORKERS} --gpu ${GPU} --exec "${EXEC}"
     ```

 11. Deploy the config to your cluster
     ```
     ks apply default 
     ```

 12. Check the pod status
     ```
     kubectl get pod -n ${NAMESPACE} -o wide
     ```

 13. Save the log
     ```
     mkdir -p results
     kubectl logs -n ${NAMESPACE} -f ${COMPONENT}-master > results/benchmark_1.out
     ```
 
 14. To iterate quickly. Remove pods, recreate openmpi component, restart from generate openmpi command
     ```
     ks delete default
     ks component rm openmpi 
     ```
 
 15. [Optional] EXEC command for 4 workers 8 GPU
     ```
     WORKERS=4
     GPU=8
     EXEC="mpiexec -np 32 --hostfile /kubeflow/openmpi/assets/hostfile --allow-run-as-root --display-map --tag-output --timestamp-output -mca btl_tcp_if_exclude lo,docker0 --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 -mca btl ^openib sh -c 'NCCL_MIN_NRINGS=8 NCCL_DEBUG=INFO python3.6 /examples/official-benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py --num_batches=100 --model vgg16 --batch_size 64 --variable_update horovod --horovod_device gpu --use_fp16'"
     ```
    
     Then follow the steps from 10-13.


 
  

