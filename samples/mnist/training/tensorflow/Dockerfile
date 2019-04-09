FROM tensorflow/tensorflow
RUN apt-get update && apt-get install -y git
RUN git clone -b r1.12.0 https://github.com/tensorflow/models.git /tmp/models
ENV PYTHONPATH="$PYTHONPATH:/tmp/models"
RUN pip install --user -r /tmp/models/official/requirements.txt

