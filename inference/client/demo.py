from flask import Flask
from flask import request, render_template
import os
from argparse import ArgumentParser
import re

"""
Send a JPEG image to tensorflow_model_server running loaded with inception model.
"""

import grpc
import tensorflow as tf

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

#server will be fixed based on the service name
tf.app.flags.DEFINE_string('server', 'localhost:9000',
                           'PredictionService host:port')
tf.app.flags.DEFINE_string('image', '', 'path to image in JPEG format')
FLAGS = tf.app.flags.FLAGS


def run_inference():
  channel = grpc.insecure_channel(FLAGS.server)
  stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
  ## Send request
  with open(FLAGS.image, 'rb') as f:
    ## See prediction_service.proto for gRPC request/response details.
    data = f.read()
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'inception'
    request.model_spec.signature_name = 'predict_images'
    request.inputs['images'].CopyFrom(
        tf.contrib.util.make_tensor_proto(data, shape=[1]))
    result = stub.Predict(request, 10.0)  # 10 secs timeout
    return result

def pre_process(s):
  indices = re.findall('string_val', s)
  l = s.split("string_val")
  predict_list = []
  for i in range(1, len(l)):
      predict_list.append(l[i].split('"')[1])
  return predict_list


#Flask Server related code
app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/',methods=['POST','GET'])
def demo():
     parser = ArgumentParser()
     parser.add_argument('--server')
     args = parser.parse_args()
     server = args.server
     if request.method == 'POST':
       file = request.files['file']
       filename=file.filename
       file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
       #Set the image and server path
       FLAGS.image=os.getcwd() + "/" + full_filename
       FLAGS.server = server 
       res=run_inference()
       #Format the string before rendering to html
       process = pre_process(str(res))
       return render_template("index.html", user_image=full_filename, user_text=res, process_text=process)
     return  render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True,  host='0.0.0.0')


