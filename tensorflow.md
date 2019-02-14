# TensorFlow on Amazon EKS

This document explains how to run TensorFlow jobs on [Amazon EKS](https://aws.amazon.com/eks/). It requires to setup KubeFlow as explained in [KubeFlow on Amazon EKS](kubeflow.md).

KubeFlow installation creates a `TFJob` custom resource. This makes it easy to run TensorFlow training jobs on Kubernetes. `tf-*` pods from the output of `kubectl get pods` verifies that.

Run TensorFlow [TfCnn example](https://github.com/tensorflow/benchmarks/tree/master/scripts/tf_cnn_benchmarks) that contains implementation of several convolutional models for image classification.

1. Create a Jsonnet representation of the job:

   ```
   export CNN_JOB_NAME=tf-cnn-training
   ks pkg install kubeflow/tf-training
   ks generate tf-job-simple-v1beta1 ${CNN_JOB_NAME} --name=${CNN_JOB_NAME}
   ```

   This will generate `components/${CNN_JOB_NAME}.jsonnet`. This is a JSON file that defines the manifest for TFJob.

2. By default, this manifest is configured to use CPU. Open `components/${CNN_JOB_NAME}.jsonnet` to customize manifest. We'll update worker to use GPUs. The diff between the generated and the updated file is shown:

   ```
   8c8,9
   < local image = "gcr.io/kubeflow/tf-benchmarks-cpu:v20171202-bdab599-dirty-284af3";
   ---
   > local image = "gcr.io/kubeflow/tf-benchmarks-gpu:v20171202-bdab599-dirty-284af3";
   >
   32,34c33,35
   <                   "--num_gpus=1",
   <                   "--local_parameter_device=cpu",
   <                   "--device=cpu",
   ---
   >                   "--num_gpus=2",
   >                   "--local_parameter_device=gpu",
   >                   "--device=gpu",
   39a41,45
   >                 resources: {
   >                   limits: {
   >                     "nvidia.com/gpu": 2
   >                   },
   >                 },
   58,60c64,66
   <                   "--num_gpus=1",
   <                   "--local_parameter_device=cpu",
   <                   "--device=cpu",
   ---
   >                   "--num_gpus=2",
   >                   "--local_parameter_device=gpu",
   >                   "--device=gpu",
   65a72,76
   >                 resources: {
   >                   limits: {
   >                     "nvidia.com/gpu": 2
   >                   },
   >                 },
   ```

   This assigns two GPUs per replica to the server and the workers.

3. `ks env list` lists the ksonnet environments available for your application. By default, it shows the output:

   ```
   ks env list
   NAME    OVERRIDE KUBERNETES-VERSION NAMESPACE SERVER
   ====    ======== ================== ========= ======
   default          v1.11.5            default   https://xxx.sk1.us-west-2.eks.amazonaws.com
   ```

   The output shows that `default` environment is configured to deploy to an EKS cluster. Setup an environment variable:

   ```
   KF_ENV=default
   ```

4. Use the updated manifest to create resources on the remote cluster:

   You can double check your job sepc `kubectl show ${KF_ENV} -c ${CNN_JOB_NAME} > /tmp/${CNN_JOB_NAME}`. We attach an [example](training/tfjob/tf_cnn_training.yaml)

   ```
   ks apply ${KF_ENV} -c ${CNN_JOB_NAME}
   INFO Applying tfjobs kubeflow.tf-cnn-training
   INFO Creating non-existent tfjobs kubeflow.tf-cnn-training
   ```

   Updated output is:

   ```
   kubectl get pods
   NAME                                                      READY   STATUS    RESTARTS   AGE
   ...
   tf-cnn-training-ps-0                                      1/1     Running   0          1m
   tf-cnn-training-worker-0                                  1/1     Running   0          1m
   ...
   ```

5. Monitor the job:

   ```
   kubectl logs tf-cnn-training-worker-0 -f
   ```

   It shows the [output](logs/tf-cnn-training-worker-0.log):

   ```
   INFO|2019-02-13T22:59:36|/opt/launcher.py|48| Launcher started.
   INFO|2019-02-13T22:59:36|/opt/launcher.py|73| Command to run: python tf_cnn_benchmarks.py --batch_size=32 --model=resnet50 --variable_update=parameter_server --flush_stdout=true --num_gpus=2 --local_parameter_device=gpu --device=gpu --data_format=NHWC --job_name=worker --ps_hosts=tf-cnn-training-ps-0.kubeflow.svc:2222 --worker_hosts=tf-cnn-training-worker-0.kubeflow.svc:2222 --task_index=0
   INFO|2019-02-13T22:59:36|/opt/launcher.py|15| Running python tf_cnn_benchmarks.py --batch_size=32 --model=resnet50 --variable_update=parameter_server --flush_stdout=true --num_gpus=2 --local_parameter_device=gpu --device=gpu --data_format=NHWC --job_name=worker --ps_hosts=tf-cnn-training-ps-0.kubeflow.svc:2222 --worker_hosts=tf-cnn-training-worker-0.kubeflow.svc:2222 --task_index=0
   INFO|2019-02-13T22:59:37|/opt/launcher.py|27| 2019-02-13 22:59:37.489630: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.177179: I tensorflow/stream_executor/cuda/cuda_gpu_executor.cc:900] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.177921: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1064] Found device 0 with properties:
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| name: Tesla V100-SXM2-16GB major: 7 minor: 0 memoryClockRate(GHz): 1.53
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| pciBusID: 0000:00:17.0
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| totalMemory: 15.78GiB freeMemory: 15.35GiB
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.485360: I tensorflow/stream_executor/cuda/cuda_gpu_executor.cc:900] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.486253: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1064] Found device 1 with properties:
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| name: Tesla V100-SXM2-16GB major: 7 minor: 0 memoryClockRate(GHz): 1.53
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| pciBusID: 0000:00:19.0
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| totalMemory: 15.78GiB freeMemory: 15.37GiB
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.486294: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1079] Device peer to peer matrix
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.486317: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1085] DMA: 0 1
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.486325: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1095] 0:   Y Y
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.486331: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1095] 1:   Y Y
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.486352: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1154] Creating TensorFlow device (/device:GPU:0) -> (device: 0, name: Tesla V100-SXM2-16GB, pci bus id: 0000:00:17.0, compute capability: 7.0)
   INFO|2019-02-13T22:59:38|/opt/launcher.py|27| 2019-02-13 22:59:38.486360: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1154] Creating TensorFlow device (/device:GPU:1) -> (device: 1, name: Tesla V100-SXM2-16GB, pci bus id: 0000:00:19.0, compute capability: 7.0)
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| 2019-02-13 23:02:11.314241: I tensorflow/core/distributed_runtime/rpc/grpc_channel.cc:215] Initialize GrpcChannelCache for job ps -> {0 -> tf-cnn-training-ps-0.kubeflow.svc:2222}
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| 2019-02-13 23:02:11.314280: I tensorflow/core/distributed_runtime/rpc/grpc_channel.cc:215] Initialize GrpcChannelCache for job worker -> {0 -> localhost:2222}
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| 2019-02-13 23:02:11.317209: I tensorflow/core/distributed_runtime/rpc/grpc_server_lib.cc:324] Started server with target: grpc://localhost:2222
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| TensorFlow:  1.5
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Model:       resnet50
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Mode:        training
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| SingleSess:  False
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Batch size:  64 global
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| 32 per device
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Devices:     ['/job:worker/task:0/gpu:0', '/job:worker/task:0/gpu:1']
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Data format: NHWC
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Optimizer:   sgd
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Variables:   parameter_server
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Sync:        True
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| ==========
   INFO|2019-02-13T23:02:11|/opt/launcher.py|27| Generating model
   INFO|2019-02-13T23:02:12|/opt/launcher.py|27| WARNING:tensorflow:From /opt/tf-benchmarks/scripts/tf_cnn_benchmarks/convnet_builder.py:372: calling reduce_mean (from tensorflow.python.ops.math_ops) with keep_dims is deprecated and will be removed in a future version.
   INFO|2019-02-13T23:02:12|/opt/launcher.py|27| Instructions for updating:
   INFO|2019-02-13T23:02:12|/opt/launcher.py|27| keep_dims is deprecated, use keepdims instead
   INFO|2019-02-13T23:02:18|/opt/launcher.py|27| 2019-02-13 23:02:18.452487: I tensorflow/core/distributed_runtime/master_session.cc:1011] Start master session 5a288b32a61167f7 with config: intra_op_parallelism_threads: 1 gpu_options { force_gpu_compatible: true } allow_soft_placement: true
   INFO|2019-02-13T23:02:20|/opt/launcher.py|27| Running warm up
   INFO|2019-02-13T23:06:30|/opt/launcher.py|27| Done warm up
   INFO|2019-02-13T23:06:30|/opt/launcher.py|27| Step	Img/sec	loss
   INFO|2019-02-13T23:06:31|/opt/launcher.py|27| 1	images/sec: 217.5 +/- 0.0 (jitter = 0.0)	10.611
   INFO|2019-02-13T23:06:33|/opt/launcher.py|27| 10	images/sec: 215.8 +/- 3.1 (jitter = 2.6)	8.493
   INFO|2019-02-13T23:06:36|/opt/launcher.py|27| 20	images/sec: 217.1 +/- 1.6 (jitter = 3.0)	8.229
   INFO|2019-02-13T23:06:39|/opt/launcher.py|27| 30	images/sec: 216.8 +/- 1.1 (jitter = 3.1)	8.105
   INFO|2019-02-13T23:06:42|/opt/launcher.py|27| 40	images/sec: 216.8 +/- 0.9 (jitter = 3.1)	7.947
   INFO|2019-02-13T23:06:45|/opt/launcher.py|27| 50	images/sec: 216.9 +/- 0.7 (jitter = 3.3)	7.916
   INFO|2019-02-13T23:06:48|/opt/launcher.py|27| 60	images/sec: 217.8 +/- 0.7 (jitter = 3.5)	8.252
   INFO|2019-02-13T23:06:51|/opt/launcher.py|27| 70	images/sec: 218.0 +/- 0.6 (jitter = 3.3)	7.880
   INFO|2019-02-13T23:06:54|/opt/launcher.py|27| 80	images/sec: 217.8 +/- 0.6 (jitter = 3.2)	7.885
   INFO|2019-02-13T23:06:57|/opt/launcher.py|27| 90	images/sec: 217.6 +/- 0.5 (jitter = 3.5)	7.823
   INFO|2019-02-13T23:07:00|/opt/launcher.py|27| 100	images/sec: 217.7 +/- 0.5 (jitter = 3.3)	7.926
   INFO|2019-02-13T23:07:00|/opt/launcher.py|27| ----------------------------------------------------------------
   INFO|2019-02-13T23:07:00|/opt/launcher.py|27| total images/sec: 217.95
   INFO|2019-02-13T23:07:00|/opt/launcher.py|27| ----------------------------------------------------------------
   INFO|2019-02-13T23:07:01|/opt/launcher.py|80| Finished: python tf_cnn_benchmarks.py --batch_size=32 --model=resnet50 --variable_update=parameter_server --flush_stdout=true --num_gpus=2 --local_parameter_device=gpu --device=gpu --data_format=NHWC --job_name=worker --ps_hosts=tf-cnn-training-ps-0.kubeflow.svc:2222 --worker_hosts=tf-cnn-training-worker-0.kubeflow.svc:2222 --task_index=0
   INFO|2019-02-13T23:07:01|/opt/launcher.py|84| Command ran successfully sleep for ever.
   ```

More details at [TensorFlow Training](https://www.kubeflow.org/docs/guides/components/tftraining/).
