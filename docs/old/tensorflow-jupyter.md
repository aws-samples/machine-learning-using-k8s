# TensorFlow Training in Jupyter Notebook

This document explains how to train TensorFlow model in JupyterNotebook on [Amazon EKS](https://aws.amazon.com/eks/). It requires to setup KubeFlow as explained in [KubeFlow on Amazon EKS](kubeflow.md) and [Jupyter](jupyterhub.md)

In this example, we will train a convolutional neural network for recognizing MNIST digits. We also like to record how the learning rate varies over time, and how the objective function is changing. Summaries will be generated during the training and it will be used to observe model in Tensorboard.

1. Create a Python3 Notebook in your Jupyter Server.

2. Write CNN training code for MNIST in notebook and train the model.

   Please check [mnist_with_summaries](samples/tensorflow/mnist_with_summaries.py)
   You need to create corresponding S3 bucket and replace credential environments variables.

3. Create TensorBoard to look at Tensorflow Graph. [TensorBoard](tensorboard.md)

> If you encounter issue like `Kernel Restarting: The kernel appears to have died. It will restart automatically.`, please increase your notebook memory. 