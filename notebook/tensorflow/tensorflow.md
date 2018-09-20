# Jupyter Notebook for TensorFlow on Amazon EKS

This document explains how to run Jupyter notebook for TensorFlow [Amazon EKS](https://aws.amazon.com/eks/). 

The good news official tensorflow docker has jupyter notebook install into it and it starts when tensorflow docker runs. The only thing needed was to do a port forwarding and using k8s logs login to jupyter notebook.

1. You can create a pod by using `k8s-machine-learning/notebook/tensorflow/tensorflow.yaml`. It uses official tensorflow docker image. 

   ```
   kubectl create -f tensorflow.yaml 
   ```

   This will create a tensorflow pod. 

2. By default when this pod runs, it has jupyter notebook running, but we need to do port-forwarding in order to access the jupyter notebook. You can use below command to map the jupyter notebook port to one of your host port


   ```
   kubectl port-forward tensorflow 8888:8888
   ```

   In general port-forwarding format is 

   ```
   kubectl port-forward <pod_name>  <host_port>:<pod_port at which your app is running>
   ```


3. Login to the Jupyter notebook. You can navigate to `127.0.0.1:8888` to access the jupyter notebook. However it will ask for the `token`. Since tensorflow container starts the jupyter notebook, if we can look at the logs we can get the token from there. 

   ```
   kubectl logs tensorflow 
   ```

   Above command will print the log of jupyter notebook start up which will include the token.

