FROM tensorflow/tensorflow 
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/fchollet/keras.git /root/keras/
RUN git clone -b 1.1.0 https://github.com/apache/incubator-mxnet.git /root/incubator-mxnet
RUN pip install keras
