# MXNet on Amazon EKS 

This document explains how to run MXNet training on [Amazon EKS](https://aws.amazon.com/eks/).

This documents assumes that you have EKS cluster available and running. You can setup 3 node cluster by following the [Amazon EKS getting started](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html)

## Single node MNIST training using MXNet on EKS
1. Get a docker image: The first requirement to get the EKS running for your application is to have a docker image. In order to run the MNIST training, docker image should have the source code of MXNet as well MXNet install into it. There is a Dockerfile available in `k8s-machine-learning/mxnet/mnist/Dockerfile` to use it.

   ```
      cd k8s-machine-learning/mxnet/mnist
      docker build . -t <tag_for_image>`
   ```

   This will generate a docker image which will have all the utility to run MNIST. You can push this generated image to docker hub in your personal repo. For convenient I have docker image available publicly with name `rgaut/deeplearning-mxnet:with_mxnet`.

2. Create a pod which will use the docker image built in step 1 and runs the MNIST training. The pod file is available at ``k8s-machine-learning/mxnet/mnist/mxnet.yaml`

   ```
      cd k8s-machine-learning/mxnet/mnist
      kubectl create -f  mxnet.yaml
   ```

   At this point you have pod running and probably soon training will start. You can check the status of pod by running `kubectl get pod mxnet` 

3. Check the progress in training. Since this is very native proof of concept we can directly get the logs from pod by running the below command 

   ```
       kubectl logs mxnet
   ``` 
   It will generate the output like below

   ```
       ....
       INFO:root:Epoch[0] Batch [800]	Speed: 39768.33 samples/sec	accuracy=0.958750
       INFO:root:Epoch[0] Batch [900]	Speed: 43640.45 samples/sec	accuracy=0.953281
       ...
   ```
