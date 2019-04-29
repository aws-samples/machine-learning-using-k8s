# Customize Kubeflow components

`${KUBEFLOW_SRC}/scripts/kfctl.sh generate k8s` will generate kubeflow suite which includes several components. Sometimes, if you just want to use few ones you already know, you can follow this guidacne to customize components you need.

If you are not familiar with [ksonnet](https://ksonnet.io/), please check out [tutorials](https://ksonnet.io/docs/tutorial/guestbook/).


1. Initialzie your ksonnet application

   ```
   export APPLICATION=eks-kubeflow-test
   export KUBEFLOW_VERSION=v0.5-branch  # use master if you want to try nightly version

   ks init ${APPLICATION}
   cd ${APPLICATION}
   ```

2. Check your existing registry and install kubeflow registry

   ```
   $ ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${KUBEFLOW_VERSION}/kubeflow
   $ ks registry list

   NAME      OVERRIDE PROTOCOL URI
   ====      ======== ======== ===
   incubator          github   github.com/ksonnet/parts/tree/master/incubator
   kubeflow           github   github.com/kubeflow/kubeflow/tree/v0.4-branch/kubeflow
   ```

3. Check packg kubeflow registry provides.

   ```
   REGISTRY  NAME                    VERSION                                  INSTALLED ENVIRONMENTS
   ========  ====                    =======                                  ========= ============
   incubator apache                  2a6bd08597dde82a3d7eb7084585b3383ba6efe0
   ...
   kubeflow  application             8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  argo                    8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  automation              8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  chainer-job             8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  common                  8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  examples                8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  gcp                     8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  jupyter                 8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  katib                   8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  kubebench               8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  metacontroller          8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  modeldb                 8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  mpi-job                 8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  mxnet-job               8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  new-package-stub        8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  nvidia-inference-server 8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  openmpi                 8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  openvino                8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  pachyderm               8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  pipeline                8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  profiles                8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  pytorch-job             8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  seldon                  8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  tensorboard             8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  tf-batch-predict        8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  tf-serving              8212d72f5a4d5edb2345cd6e93c6231c15db2976
   kubeflow  tf-training             8212d72f5a4d5edb2345cd6e93c6231c15db2976
   ```

4. `common` is required to power other pkgs so this is a required package. Let's say we want to deploy tensorflow operator here. It's insde `tf-training`, let's install these two packages.
   ```
   $ ks pkg install kubeflow/common
   INFO Retrieved 17 files

   $ ks pkg install kubeflow/tf-training
   INFO Retrieved 4 files
   ```

5. Once we have packages, let's generate prototypes
   ```
   $ ks prototype list

   NAME                                  DESCRIPTION
   ====                                  ===========
   io.ksonnet.pkg.ambassador             Ambassador
   io.ksonnet.pkg.centraldashboard       centraldashboard
   io.ksonnet.pkg.configMap              A simple config map with optional user-specified data
   io.ksonnet.pkg.deployed-service       A deployment exposed with a service
   io.ksonnet.pkg.echo-server            A simple echo server.
   io.ksonnet.pkg.namespace              Namespace with labels automatically populated from the name
   io.ksonnet.pkg.single-port-deployment Replicates a container n times, exposes a single port
   io.ksonnet.pkg.single-port-service    Service that exposes a single port
   io.ksonnet.pkg.spartakus              spartakus component for usage collection
   io.ksonnet.pkg.tf-job-operator        A TensorFlow job operator.
   ```

6. Generate component from prototype and deploy manifest
   ```
   $ export COMPONENT_NAME=my-tf-job-operator
   $ ks generate tf-job-operator ${COMPONENT_NAME}
   INFO Writing component at '/tmp/eks-kubeflow-test/components/my-tf-job-operator.jsonnet'


   $ ks component list

   COMPONENT          TYPE    APIVERSION KIND NAME
   =========          ====    ========== ==== ====
   my-tf-job-operator jsonnet


   $ ks param set ${COMPONENT_NAME} deploymentNamespace default # customize your component

   $ ks env list

   NAME    OVERRIDE KUBERNETES-VERSION NAMESPACE SERVER
   ====    ======== ================== ========= ======
   default          v1.11.5            default   https://xxx.sk1.us-west-2.eks.amazonaws.com


   $ ks apply default -c ${COMPONENT_NAME}

   INFO Applying customresourcedefinitions tfjobs.kubeflow.org
   INFO Applying serviceaccounts default.tf-job-dashboard
   INFO Creating non-existent serviceaccounts default.tf-job-dashboard
   INFO Applying configmaps default.tf-job-operator-config
   INFO Creating non-existent configmaps default.tf-job-operator-config
   INFO Applying serviceaccounts default.tf-job-operator
   INFO Creating non-existent serviceaccounts default.tf-job-operator
   INFO Applying clusterroles tf-job-operator
   INFO Applying clusterrolebindings tf-job-operator
   INFO Applying services default.tf-job-dashboard
   INFO Creating non-existent services default.tf-job-dashboard
   INFO Applying clusterroles tf-job-dashboard
   INFO Applying clusterrolebindings tf-job-dashboard
   INFO Applying deployments default.tf-job-operator-v1beta1
   INFO Creating non-existent deployments default.tf-job-operator-v1beta1
   INFO Applying deployments default.tf-job-dashboard
   INFO Creating non-existent deployments default.tf-job-dashboard
   ```

7. Verify pod status
   ```
   $ kubectl get pods

   NAME                                       READY   STATUS    RESTARTS   AGE
   tf-job-dashboard-5f986cf99d-lnk46          1/1     Running   0          1m
   tf-job-operator-v1beta1-5876c48976-pcjs9   1/1     Running   0          1m
   ```