# Build image:
# docker build -t seedjeffwan/mnist_tensorflow_keras:1.13.1 .
#
# 1. Without saving summary and export mode, run
# docker run seedjeffwan/mnist_tensorflow_keras:1.13.1
#
# 2. Export model summary and saved model, run
# docker run
# -e AWS_ACCESS_KEY_ID=your_access_key_id \
# -e AWS_SECRET_ACCESS_KEY=your_access_key_id \
# -e AWS_REGION=us-west-2 \
# seedjeffwan/mnist_tensorflow_keras:1.13.1 \
# python mnist.py \
# --model_export_path s3://kubeflow-pipeline-data/mnist/export \
# --model_summary_path s3://kubeflow-pipeline-data/mnist/summary \
# --epochs 5

FROM tensorflow/tensorflow:1.13.1

COPY mnist.py /mnist.py

CMD [ "python", "mnist.py" ]