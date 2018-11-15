FROM  tensorflow/tensorflow:1.10.0 
WORKDIR "/root"
RUN apt-get update 
RUN apt-get install git -y
RUN pip install --upgrade pip
RUN pip install flask 
RUN pip install grpcio
RUN pip install tensorflow-serving-api
RUN git clone  https://github.com/tensorflow/serving
RUN cd serving && git checkout tags/1.10.0
COPY demo.py /root
COPY static /root/static
COPY templates /root/templates 
ENTRYPOINT ["/bin/bash"]
