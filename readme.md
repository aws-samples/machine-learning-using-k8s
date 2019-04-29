# Machine Learning Frameworks on Kubernetes

This repository explains how to run different Machine Learning frameworks on [Amazon EKS](https://aws.amazon.com/eks).

- [Create GPU-enabled Amazon EKS cluster with Kubeflow](docs/eks-gpu.md)
- Single node training for MNIST
  - [TensorFlow and Keras on Amazon EKS](docs/mnist/training/tensorflow.md)
  - [MXNet on Amazon EKS](docs/mnist/training/mxnet.md)
- Inference for MNIST
  - [TensorFlow Serving Component](docs/mnist/inference/tensorflow.md)
  - [MXNet Model Server](docs/mnist/inference/mxnet.md)
- TensorBoard setup
  - [TensorBoard on Amazon EKS](docs/tensorboard/readme.md)

## Other Notes

- [Jupyter Notebook on Amazon EKS](docs/jupyterhub/readme.md)
- Distributed training
  - [TensorFlow and Horovod on Amazon EKS with ImageNet Data](docs/imagenet/training/tensorflow-horovod.md)
  - [TensorFlow and Horovod on Amazon EKS with Synthetic Data](docs/imagenet/training/tensorflow-horovod-synthetic.md)
- Inference using Imagenet
    - [TensorFlow on Amazon EKS](docs/imagenet/inference/tensorflow.md)
