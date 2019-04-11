# Training MNIST using TensorFlow and Keras on Amazon EKS

This document exaplins how to build a MNIST model using TensorFlow and Keras on Amazon EKS.

This documents assumes that you have an EKS cluster available and running. Make sure to have a [GPU-enabled Amazon EKS cluster](eks-gpu.md) ready.

## MNIST training using TensorFlow on EKS

In this sample, we'll use MNIST database of handwritten digits and train the model to recognize any handwritten digit.

1. You can use a pre-built Docker image `rgaut/deeplearning-tensorflow:with_model`. This image uses `tensorflow/tensorflow` as the base image. It comes bundled with TensorFlow. It also has training code and downloads training and test data sets. It also stores the model using a volume mount `/mount`. This maps to `/tmp` directory on the worker node.

   Alternatively, you can build a Docker image using the Dockerfile in `samples/mnist/training/tensorflow/Dockerfile` to build it. This Dockerfile uses [AWS Deep Learning Containers](https://aws.amazon.com/machine-learning/containers/). Accessing this image requires that you login to the ECR repository:

   ```
   $(aws ecr get-login --no-include-email --region us-east-1 --registry-ids 763104351884)
   ```
 
   Then the Docker image can be built:

   ```
   docker build -t <dockerhub_username>/<repo_name>:<tag_name> .
   ```

   This will create a Docker image that will have all the utilities to run MNIST.

2. Create a pod that will use this Docker image and run the MNIST training:

   ```
   kubectl create -f samples/mnist/training/tensorflow/tensorflow.yaml
   ```

   This will start the pod and start the training. Check status:

   ```
   kubectl get pod tensorflow -w
   NAME         READY   STATUS    RESTARTS   AGE
   tensorflow   1/1     Running   0          25s
   ```

   This will also dump the generated model at `/model` on the worker node. This is causing https://github.com/aws-samples/machine-learning-using-k8s/issues/53.

3. Check the progress in training:

	```
	2019-04-10 20:33:56.216636: I tensorflow/core/platform/cpu_feature_guard.cc:141] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
	2019-04-10 20:33:56.234259: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 2300065000 Hz
	2019-04-10 20:33:56.236236: I tensorflow/compiler/xla/service/service.cc:150] XLA service 0x4f82540 executing computations on platform Host. Devices:
	2019-04-10 20:33:56.236262: I tensorflow/compiler/xla/service/service.cc:158]   StreamExecutor device (0): <undefined>, <undefined>
	I0410 20:33:56.678050 140629992953600 run_config.py:532] Initializing RunConfig with distribution strategies.
	I0410 20:33:56.678266 140629992953600 estimator_training.py:166] Not using Distribute Coordinator.
	I0410 20:33:56.678631 140629992953600 estimator.py:201] Using config: {'_save_checkpoints_secs': 600, '_session_config': allow_soft_placement: true
	, '_keep_checkpoint_max': 5, '_task_type': 'worker', '_train_distribute': <tensorflow.contrib.distribute.python.one_device_strategy.OneDeviceStrategy object at 0x7fe6901f3650>, '_is_chief': True, '_cluster_spec': <tensorflow.python.training.server_lib.ClusterSpec object at 0x7fe6901f3610>, '_model_dir': '/tmp/mnist_model', '_protocol': None, '_save_checkpoints_steps': None, '_keep_checkpoint_every_n_hours': 10000, '_service': None, '_num_ps_replicas': 0, '_tf_random_seed': None, '_save_summary_steps': 100, '_device_fn': None, '_experimental_distribute': None, '_num_worker_replicas': 1, '_task_id': 0, '_log_step_count_steps': 100, '_evaluation_master': '', '_eval_distribute': None, '_global_id_in_cluster': 0, '_master': '', '_distribute_coordinator_mode': None}
	W0410 20:33:57.322146 140629992953600 deprecation.py:323] From /tmp/models/official/mnist/dataset.py:100: to_int32 (from tensorflow.python.ops.math_ops) is deprecated and will be removed in a future version.
	Instructions for updating:
	Use tf.cast instead.

	. . .

	I0410 20:34:27.340025 140629992953600 basic_session_run_hooks.py:247] loss = 0.17755193, step = 500 (4.791 sec)
	I0410 20:34:32.069824 140629992953600 basic_session_run_hooks.py:594] Saving checkpoints for 600 into /tmp/mnist_model/model.ckpt.
	I0410 20:34:32.147376 140629992953600 util.py:168] Finalize strategy.
	I0410 20:34:32.215636 140629992953600 estimator.py:359] Loss for final step: 0.20872988.
	I0410 20:34:32.445682 140629992953600 estimator.py:1111] Calling model_fn.
	I0410 20:34:32.593489 140629992953600 estimator.py:1113] Done calling model_fn.
	I0410 20:34:32.611218 140629992953600 evaluation.py:257] Starting evaluation at 2019-04-10T20:34:32Z

	. . .

	I0410 20:58:12.440040 140629992953600 basic_session_run_hooks.py:247] loss = 0.0003796204, step = 23300 (4.807 sec)
	I0410 20:58:17.192491 140629992953600 basic_session_run_hooks.py:594] Saving checkpoints for 23400 into /tmp/mnist_model/model.ckpt.
	I0410 20:58:17.276602 140629992953600 util.py:168] Finalize strategy.
	I0410 20:58:17.342698 140629992953600 estimator.py:359] Loss for final step: 0.00014415917.
	I0410 20:58:17.382083 140629992953600 estimator.py:1111] Calling model_fn.
	I0410 20:58:17.536731 140629992953600 estimator.py:1113] Done calling model_fn.
	I0410 20:58:17.555907 140629992953600 evaluation.py:257] Starting evaluation at 2019-04-10T20:58:17Z
	I0410 20:58:17.634746 140629992953600 monitored_session.py:222] Graph was finalized.

	. . .

	Downloading https://storage.googleapis.com/cvdf-datasets/mnist/train-images-idx3-ubyte.gz to /tmp/tmpZ7F4sN.gz
	Downloading https://storage.googleapis.com/cvdf-datasets/mnist/train-labels-idx1-ubyte.gz to /tmp/tmpT_nF_V.gz
	Downloading https://storage.googleapis.com/cvdf-datasets/mnist/t10k-images-idx3-ubyte.gz to /tmp/tmpBTphwd.gz
	Downloading https://storage.googleapis.com/cvdf-datasets/mnist/t10k-labels-idx1-ubyte.gz to /tmp/tmp1qgKBN.gz

	Evaluation results:
		{'loss': 0.10796012, 'global_step': 600, 'accuracy': 0.9674}


	. . .

	Evaluation results:
		{'loss': 0.027667878, 'global_step': 22200, 'accuracy': 0.9923}


	Evaluation results:
		{'loss': 0.026092911, 'global_step': 22800, 'accuracy': 0.9928}

	. . .

	I0410 20:58:57.740638 140629992953600 saver.py:1270] Restoring parameters from /tmp/mnist_model/model.ckpt-24000
	I0410 20:58:57.759921 140629992953600 builder_impl.py:654] Assets added to graph.
	I0410 20:58:57.760041 140629992953600 builder_impl.py:449] No assets to write.
	I0410 20:58:57.806967 140629992953600 builder_impl.py:414] SavedModel written to: /model/temp-1554929937/saved_model.pb
		{'loss': 0.025196994, 'global_step': 23400, 'accuracy': 0.9936}


	Evaluation results:
		{'loss': 0.031494826, 'global_step': 24000, 'accuracy': 0.9923}
	```

## What happened?

- Runs `/tmp/models/official/mnist/mnist.py` command (specified in the Dockerfile and available at https://github.com/tensorflow/models/blob/master/official/mnist/mnist.py)
  - Downloads MNIST training and test data set
    - Each set has images and labels that identify the image
  - Performs supervised learning
    - Run 40 epochs using the training data with the specified parameters
    - For each epoch
      - Reads the training data
      - Builds the training model using the specified algorithm
      - Feeds the test data and matches with the expected output
      - Reports the accuracy, expected to improve with each run
  	- A checkpoint is saved every 600 seconds

