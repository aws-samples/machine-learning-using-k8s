# TensorFlow on Amazon EKS

This document explains how to run TensorFlow jobs on [Amazon EKS](https://aws.amazon.com/eks/). It requires to setup KubeFlow as explained in [KubeFlow on Amazon EKS](kubeflow.md).

KubeFlow installation creates a `TFJob` custom resource. This makes it easy to run TensorFlow training jobs on Kubernetes. `tf-*` pods from the output of `kubectl get pods` verifies that.

Run TensorFlow [TfCnn example](https://github.com/tensorflow/benchmarks/tree/master/scripts/tf_cnn_benchmarks) that contains implementation of several convolutional models for image classification.

1. Create a Jsonnet representation of the job:

   ```
   ks init hello
   CNN_JOB_NAME=mycnnjob
   VERSION=v0.2-branch
   ks registry add kubeflow-git github.com/kubeflow/kubeflow/tree/${VERSION}/kubeflow
   ks pkg install kubeflow-git/examples
   ks generate tf-job-simple ${CNN_JOB_NAME} --name=${CNN_JOB_NAME}
   ```

   This will generate `components/${CNN_JOB_NAME}.jsonnet`. This is a JSON file that defines the manifest for TFJob.

2. By default, this manifest is configured to use CPU. We'll update this to use GPUs. The diff between the generated and the updated file is shown:

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
   default          v1.10.3            default   https://1E7360C77135B57E36AF7DAB726206C2.sk1.us-west-2.eks.amazonaws.com
   ```

   The output shows that `default` environment is configured to deploy to an EKS cluster. Setup an environment variable:

   ```
   KF_ENV=default
   ```

4. Use the updated manifest to create resources on the remote cluster:

   ```
   ks apply ${KF_ENV} -c ${CNN_JOB_NAME}
   INFO Applying tfjobs default.mycnnjob             
   INFO Creating non-existent tfjobs default.mycnnjob
   ```

   Updated output is:

   ```
   kubectl get pods
   NAME                                        READY     STATUS    RESTARTS   AGE
   ambassador-59cb5ccd89-bgbpc                 2/2       Running   0          1d
   ambassador-59cb5ccd89-wkf76                 2/2       Running   0          1d
   ambassador-59cb5ccd89-wvdz9                 2/2       Running   0          1d
   centraldashboard-7d7744cccb-g6hcn           1/1       Running   0          1d
   mycnnjob-ps-0                               1/1       Running   0          4s
   mycnnjob-worker-0                           1/1       Running   0          4s
   spartakus-volunteer-8bf586df9-xdtqf         1/1       Running   0          1d
   tf-hub-0                                    1/1       Running   0          1d
   tf-job-dashboard-bfc9bc6bc-h5lql            1/1       Running   0          1d
   tf-job-operator-v1alpha2-756cf9cb97-rkdtv   1/1       Running   0          1d
   ```

5. Monitor the job:

   ```
   kubectl logs mycnnjob-worker-0 -f
   ```

   It shows the output:

   ```
   INFO|2018-09-14T21:50:27|/opt/launcher.py|48| Launcher started.
   INFO|2018-09-14T21:50:27|/opt/launcher.py|73| Command to run: python tf_cnn_benchmarks.py --batch_size=32 --model=resnet50 --variable_update=parameter_server --flush_stdout=true --num_gpus=2 --local_parameter_device=gpu --device=gpu --data_format=NHWC --job_name=worker --ps_hosts=mycnnjob-ps-0.default.svc.cluster.local:2222 --worker_hosts=mycnnjob-worker-0.default.svc.cluster.local:2222 --task_index=0
   INFO|2018-09-14T21:50:27|/opt/launcher.py|15| Running python tf_cnn_benchmarks.py --batch_size=32 --model=resnet50 --variable_update=parameter_server --flush_stdout=true --num_gpus=2 --local_parameter_device=gpu --device=gpu --data_format=NHWC --job_name=worker --ps_hosts=mycnnjob-ps-0.default.svc.cluster.local:2222 --worker_hosts=mycnnjob-worker-0.default.svc.cluster.local:2222 --task_index=0
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.028924: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.192614: I tensorflow/stream_executor/cuda/cuda_gpu_executor.cc:900] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.193148: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1064] Found device 0 with properties:
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| name: Tesla V100-SXM2-16GB major: 7 minor: 0 memoryClockRate(GHz): 1.53
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| pciBusID: 0000:00:1d.0
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| totalMemory: 15.78GiB freeMemory: 15.37GiB
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.299658: I tensorflow/stream_executor/cuda/cuda_gpu_executor.cc:900] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.300181: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1064] Found device 1 with properties:
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| name: Tesla V100-SXM2-16GB major: 7 minor: 0 memoryClockRate(GHz): 1.53
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| pciBusID: 0000:00:1e.0
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| totalMemory: 15.78GiB freeMemory: 15.37GiB
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.300222: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1079] Device peer to peer matrix
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.300240: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1085] DMA: 0 1
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.300247: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1095] 0:   Y Y
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.300252: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1095] 1:   Y Y
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.300265: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1154] Creating TensorFlow device (/device:GPU:0) -> (device: 0, name: Tesla V100-SXM2-16GB, pci bus id: 0000:00:1d.0, compute capability: 7.0)
   INFO|2018-09-14T21:50:29|/opt/launcher.py|27| 2018-09-14 21:50:29.300273: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1154] Creating TensorFlow device (/device:GPU:1) -> (device: 1, name: Tesla V100-SXM2-16GB, pci bus id: 0000:00:1e.0, compute capability: 7.0)
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| 2018-09-14 21:53:05.692585: I tensorflow/core/distributed_runtime/rpc/grpc_channel.cc:215] Initialize GrpcChannelCache for job ps -> {0 -> mycnnjob-ps-0.default.svc.cluster.local:2222}
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| 2018-09-14 21:53:05.692618: I tensorflow/core/distributed_runtime/rpc/grpc_channel.cc:215] Initialize GrpcChannelCache for job worker -> {0 -> localhost:2222}
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| 2018-09-14 21:53:05.694549: I tensorflow/core/distributed_runtime/rpc/grpc_server_lib.cc:324] Started server with target: grpc://localhost:2222
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| TensorFlow:  1.5
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Model:       resnet50
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Mode:        training
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| SingleSess:  False
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Batch size:  64 global
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| 32 per device
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Devices:     ['/job:worker/task:0/gpu:0', '/job:worker/task:0/gpu:1']
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Data format: NHWC
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Optimizer:   sgd
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Variables:   parameter_server
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Sync:        True
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| ==========
   INFO|2018-09-14T21:53:05|/opt/launcher.py|27| Generating model
   INFO|2018-09-14T21:53:07|/opt/launcher.py|27| WARNING:tensorflow:From /opt/tf-benchmarks/scripts/tf_cnn_benchmarks/convnet_builder.py:372: calling reduce_mean (from tensorflow.python.ops.math_ops) with keep_dims is deprecated and will be removed in a future version.
   INFO|2018-09-14T21:53:07|/opt/launcher.py|27| Instructions for updating:
   INFO|2018-09-14T21:53:07|/opt/launcher.py|27| keep_dims is deprecated, use keepdims instead
   INFO|2018-09-14T21:53:11|/opt/launcher.py|27| 2018-09-14 21:53:11.639189: I tensorflow/core/distributed_runtime/master_session.cc:1011] Start master session 08ac08909768fc95 with config: intra_op_parallelism_threads: 1 gpu_options { force_gpu_compatible: true } allow_soft_placement: true
   INFO|2018-09-14T21:53:13|/opt/launcher.py|27| Running warm up
   INFO|2018-09-14T21:57:36|/opt/launcher.py|27| Done warm up
   INFO|2018-09-14T21:57:36|/opt/launcher.py|27| Step Img/sec  loss
   INFO|2018-09-14T21:57:36|/opt/launcher.py|27| 1 images/sec: 151.0 +/- 0.0 (jitter = 0.0)  9.583
   INFO|2018-09-14T21:57:40|/opt/launcher.py|27| 10   images/sec: 168.2 +/- 2.0 (jitter = 1.0)  8.411
   INFO|2018-09-14T21:57:44|/opt/launcher.py|27| 20   images/sec: 164.8 +/- 2.3 (jitter = 5.3)  8.226
   INFO|2018-09-14T21:57:48|/opt/launcher.py|27| 30   images/sec: 164.3 +/- 1.6 (jitter = 4.9)  8.251
   INFO|2018-09-14T21:57:52|/opt/launcher.py|27| 40   images/sec: 163.1 +/- 1.3 (jitter = 4.0)  8.076
   INFO|2018-09-14T21:57:56|/opt/launcher.py|27| 50   images/sec: 162.9 +/- 1.1 (jitter = 5.7)  8.017
   INFO|2018-09-14T21:58:00|/opt/launcher.py|27| 60   images/sec: 162.6 +/- 0.9 (jitter = 5.2)  8.083
   INFO|2018-09-14T21:58:04|/opt/launcher.py|27| 70   images/sec: 162.3 +/- 0.9 (jitter = 4.7)  7.916
   INFO|2018-09-14T21:58:08|/opt/launcher.py|27| 80   images/sec: 162.2 +/- 0.8 (jitter = 4.9)  7.991
   INFO|2018-09-14T21:58:12|/opt/launcher.py|27| 90   images/sec: 162.4 +/- 0.7 (jitter = 4.1)  7.836
   INFO|2018-09-14T21:58:16|/opt/launcher.py|27| 100  images/sec: 162.2 +/- 0.6 (jitter = 3.9)  7.940
   INFO|2018-09-14T21:58:16|/opt/launcher.py|27| ----------------------------------------------------------------
   INFO|2018-09-14T21:58:16|/opt/launcher.py|27| total images/sec: 162.34
   INFO|2018-09-14T21:58:16|/opt/launcher.py|27| ----------------------------------------------------------------
   INFO|2018-09-14T21:58:16|/opt/launcher.py|80| Finished: python tf_cnn_benchmarks.py --batch_size=32 --model=resnet50 --variable_update=parameter_server --flush_stdout=true --num_gpus=2 --local_parameter_device=gpu --device=gpu --data_format=NHWC --job_name=worker --ps_hosts=mycnnjob-ps-0.default.svc.cluster.local:2222 --worker_hosts=mycnnjob-worker-0.default.svc.cluster.local:2222 --task_index=0
   ```

More details at [TensorFlow Training](https://www.kubeflow.org/docs/guides/components/tftraining/).

## Open Questions

- Setup `VERSION=master` and try it

