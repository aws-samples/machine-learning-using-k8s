# Machine Learning Frameworks on Kubernetes

This repository explains how to run different Machine Learning frameworks on [Amazon EKS](https://aws.amazon.com/eks).

- [Create GPU-enabled Amazon EKS cluster](eks-gpu.md)
- [Setup KubeFlow on Amazon EKS](kubeflow.md)
- [Jupyter Notebook on Amazon EKS](jupyterhub.md)
- Training
  - Single node training for MNIST
    - [TensorFlow + Keras on Amazon EKS](tensorflow-keras.md)
    - [MXNet on Amazon EKS](mxnet.md)  
  - Distributed training
    - [TensorFlow and Horovod on Amazon EKS with ImageNet Data](tensorflow-horovod-imagenet.md)
    - [TensorFlow and Horovod on Amazon EKS with Synthetic Data](tensorflow-horovod-synthetic.md)
- Inference
  - [MNIST using TensorFlow Serving Component](tensorflow-inference-kubeflow.md)
  - [Image Recognition using TensorFlow on Amazon EKS](tensorflow-inference.md)
- TensorBoard setup
  - [TensorBoard on Amazon EKS](tensorboard.md)
