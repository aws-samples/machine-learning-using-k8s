# Jupyter Notebook on Amazon EKS

This document explains how to run a Jupyter notebook for model development on [Amazon EKS](https://aws.amazon.com/eks/). 

Jupyter Notebook (previously named IPython Notebook) and JupyterLab are user interfaces for computational science and data science commonly used with Spark, Tensorflow and other big data processing frameworks. They are used by data scientists and ML engineers across a variety of organizations for interactive tasks.

JupyterHub lets users manage authenticated access to multiple single-user Jupyter notebooks. 

Kubeflow already integrate wtih JupyterHub and the only thing needed was to do a port forwarding and spawn a Jupyter Notebook. 

1. Get access to Kubeflow UI

   ```
   export NAMESPACE=kubeflow
   kubectl port-forward svc/ambassador -n ${NAMESPACE} 8080:80
   ```
   
   Now you can access the central navigation dashboard at
   ```
   http://localhost:8080/
   ```

2. Click JupyterHub tab and navigate to spawner. 

3. Sign in JupyterHub
   Right now, EKS doesn't integrate authentication solution with JupyterHub, you can type any username and password combination to bypass authentication. 

4. Configure Spawner
   a. Choose the right framework image. if you prefer to use other framework like MXNet, PyTorch, you can also build your own image. Let's choose `gcr.io/kubeflow-images-public/tensorflow-1.12.0-notebook-gpu:v0.4.0`

   b. Click `Toggle Advanced` to advanced settings.
     - Add Workpace volume if you need perisist your workplace notebooks after jupyter notebook destroyed.
     - Add Data Volumns if you want to train with large datasets.
     - Add GPU resources if your cluster has accelerator nodes and GPU image is choosen.
     ![Jupyter Spawner Configuration](images/jupyter-spawner-configuration.png)

5. Click `Spawn` button to create your customized Jupyter notebook. This may take few minutes.

> Debug your  `kubectl -n ${NAMESPACE} describe pods jupyter-${USERNAME}`

6. Once your server starts up. Verify docker image working properly.
   
   Check Tensorflow version
   ```
   import tensorflow as tf
   tf.__version__
   ```

   Check GPU allocated to Jupyter Notebook
   ```
   from tensorflow.python.client import device_lib
   print(device_lib.list_local_devices())
   ```
   ![Jupyter Verification](images/jupyter-verification.png)

   Create a terminal to monitor nvidia device
   ```
   $ nvidia-smi
   Mon Feb 11 19:46:02 2019
   +-----------------------------------------------------------------------------+
   | NVIDIA-SMI 396.26                 Driver Version: 396.26                    |
   |-------------------------------+----------------------+----------------------+
   | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
   | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
   |===============================+======================+======================|
   |   0  Tesla V100-SXM2...  On   | 00000000:00:1E.0 Off |                    0 |
   | N/A   41C    P0    39W / 300W |    994MiB / 16160MiB |      0%      Default |
   +-------------------------------+----------------------+----------------------+

   +-----------------------------------------------------------------------------+ 
   | Processes:                                                       GPU Memory |
   |  GPU       PID   Type   Process name                             Usage      |
   |=============================================================================|
   +-----------------------------------------------------------------------------+
   ```
7. Destroy your notebook.

   One user can only have one Jupyter Notebook running. In order to use a different notebook or destroy your notebook, you have to stop existing server first.  
   Click `Control Panel` button on the right top of Jupyter Notebook. Click `Stop My Server` button to destroy the server.

   > Note: Persistent Volume won't be deleted in case you want to restore your notebooks.