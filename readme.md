# Machine Learning Frameworks on Kubernetes

This repository explains how to run different Machine Learning frameworks on [Amazon EKS](https://aws.amazon.com/eks).

- [Create GPU-enabled Amazon EKS cluster with Kubeflow](docs/eks-gpu.md)
- Single node training for MNIST
  - [TensorFlow and Keras](docs/mnist/training/tensorflow.md)
  - [MXNet and Keras](docs/mnist/training/mxnet.md)
- Inference for MNIST
  - [TensorFlow Serving Component](docs/mnist/inference/tensorflow.md)
  - [MXNet Model Server](docs/mnist/inference/mxnet.md)
- TensorBoard setup
  - [TensorBoard on Amazon EKS](docs/tensorboard/readme.md)
- Distributed training
  - [TensorFlow and Horovod on Amazon EKS with ImageNet Data](docs/imagenet/training/tensorflow-horovod.md)
  - [TensorFlow and Horovod on Amazon EKS with Synthetic Data](docs/imagenet/training/tensorflow-horovod-synthetic.md)
  - [MNIST Handwritten Digit Recognition in PyTorch](docs/mnist/training/pytorch.md)

## Other Notes

- [Jupyter Notebook on Amazon EKS](docs/jupyterhub/readme.md)
- Serverless Inference
  - [Serverless inference on AWS Fargate](docs/serverlss/inference/readme.md)
- Inference using Imagenet
    - [TensorFlow on Amazon EKS](docs/imagenet/inference/tensorflow.md)
