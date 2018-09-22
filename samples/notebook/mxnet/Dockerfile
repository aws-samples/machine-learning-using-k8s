FROM mxnet/python:gpu

RUN apt-get update && apt-get install -y python-dev && apt-get install -y python3-dev

RUN pip --no-cache-dir install \
        Pillow \
        h5py \
        ipykernel \
        jupyter \
        keras_applications==1.0.5 \
        keras_preprocessing==1.0.3 \
        matplotlib \
        numpy \
        pandas \
        scipy \
        sklearn \
        && \
    python -m ipykernel.kernelspec


# Set up our notebook config.
COPY jupyter_notebook_config.py /root/.jupyter/

# Copy sample notebook
COPY mxnet-tutorial /mxnet-tutorial

#Start jupyter notebook script
COPY run_jupyter.sh /

# IPython
EXPOSE 8888

WORKDIR "/mxnet-tutorial"

ENTRYPOINT ["/bin/bash", "-c", "/run_jupyter.sh --ip=127.0.0.1 --allow-root"]
