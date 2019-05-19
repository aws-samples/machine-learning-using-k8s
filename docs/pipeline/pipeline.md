# Run Machine Learning Pipelines in Hybrid Environment using Kubeflow Pipelines

Kubeflow Pipeline uses Argo workflow (https://github.com/argoproj/argo) underneath and Argo workflow is container-native workflow engine for orchestrating parallel jobs on Kubernetes.

When running workflows, it is very common to have steps that generate or consume artifacts (https://github.com/argoproj/argo/blob/master/examples/README.md#artifacts). Often, the output artifacts of one step may be used as input artifacts to a subsequent step. Output parameters (https://github.com/argoproj/argo/blob/master/examples/README.md#output-parameters) provide a general mechanism to use the result of a step as a parameter rather than as an artifact. With output parameters and artifacts support, we can generate results in every step and consume results in following steps and build a DAG workflow. We can leverage S3 to store intermediate results and final outputs.

Ideal case is to choose components based on your needs, for example, for data preprocessing part, some users prefer to use Spark to do ETL jobs; for distributed training, users may like to leverage k8s to train the model, some user will consider use hosted AWS Service SageMaker to train the model.

## Reusable components

- [Elastic Map Reduce](https://aws.amazon.com/emr/)
- [SageMaker](https://aws.amazon.com/sagemaker/)
- [Athena](https://aws.amazon.com/athena/)


## Examples
- [Mnist Classification using SageMaker](https://github.com/kubeflow/pipelines/blob/master/samples/aws-samples/mnist-kmeans-sagemaker/mnist-classification-pipeline.py)

- [Titanic Survival Prediction](https://github.com/kubeflow/pipelines/tree/master/samples/aws-samples/titanic-survival-prediction)
