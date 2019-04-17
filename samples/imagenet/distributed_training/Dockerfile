FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/tensorflow-training:1.13-horovod-gpu-py27-cu100-ubuntu16.04

RUN mkdir /tensorflow
WORKDIR "/tensorflow"
RUN git clone -b cnn_tf_v1.12_compatible https://github.com/tensorflow/benchmarks
WORKDIR "/tensorflow/benchmarks"

CMD mpirun \
  python scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py \
    --model resnet101 \
    --batch_size 64 \
    --variable_update horovod
