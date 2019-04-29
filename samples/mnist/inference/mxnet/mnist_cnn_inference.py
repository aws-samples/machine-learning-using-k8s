# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#     http://www.apache.org/licenses/LICENSE-2.0
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import mxnet as mx
import json
import os
import logging


class MXNetVisionServiceBatching(object):
    def __init__(self):
        """
        Initialization for MXNet Vision Service supporting batch inference
        """
        self.mxnet_ctx = None
        self.mx_model = None
        self.labels = None
        self.epoch = 0
        self._context = None
        self._batch_size = 0
        self.initialized = False
        self.erroneous_reqs = set()

    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time

        :param context: Initial context contains model server system properties.
        :return:
        """
        self._context = context
        self._batch_size = context.system_properties["batch_size"] if context is not None else "1"
        self.initialized = True

        properties = context.system_properties if context is not None \
            else {"model_dir": os.getcwd()}
        model_dir = properties.get("model_dir")
        gpu_id = properties.get("gpu_id")

        model_files_prefix = context.manifest["model"]["modelName"] if context is not None else "mnist_cnn"

        data_names = ["/conv2d_1_input1"]
        data_shapes = [(data_names[0], (1, 28, 28, 1))]

        checkpoint_prefix = "{}/{}".format(model_dir, model_files_prefix)

        # Load MXNet module
        self.mxnet_ctx = mx.cpu() if gpu_id is None else mx.gpu(gpu_id)
        sym, arg_params, aux_params = mx.model.load_checkpoint(checkpoint_prefix, self.epoch)

        # noinspection PyTypeChecker
        self.mx_model = mx.mod.Module(symbol=sym, context=self.mxnet_ctx,
                                      data_names=data_names, label_names=None)
        self.mx_model.bind(for_training=False, data_shapes=data_shapes)
        self.mx_model.set_params(arg_params, aux_params, allow_missing=True, allow_extra=True)

    def inference(self, model_input):
        """
        Internal inference methods for MXNet. Run forward computation and
        return output.

        :param model_input: list of NDArray
            Preprocessed inputs in NDArray format.
        :return: list of NDArray
            Inference output.
        """
        data_iter = mx.io.NDArrayIter(model_input, None, 1)
        outputs = self.mx_model.predict(data_iter)
        res = mx.ndarray.split(outputs[0], axis=0, num_outputs=outputs[0].shape[0])
        return res

    def preprocess(self, request):
        """
        Decode all input images into ndarray.

        Note: This implementation doesn't properly handle error cases in batch mode,
        If one of the input images is corrupted, all requests in the batch will fail.

        :param request:
        :return:
        """
        img_list = []
        param_name = "/conv2d_1_input1"
        input_shape = [128, 28, 28, 1]  # Channels last

        h = input_shape[1]
        w = input_shape[2]

        for idx, data in enumerate(request):
            img = data.get(param_name)
            if img is None:
                img = data.get("body")

            if img is None:
                img = data.get("data")

            if img is None or len(img) == 0:
                logging.error("Error processing request")
                self.erroneous_reqs.add(idx)
                continue

            try:
                img_arr = mx.image.imdecode(img, 0, True, None)
            except Exception as e:
                logging.error(e, exc_info=True)
                raise

            img_arr = mx.image.imresize(img_arr, w, h)
            img_arr = img_arr.astype("float32")
            img_arr /= 255
            img_list.append(img_arr)

        reqs = mx.nd.stack(*img_list)
        reqs = reqs.as_in_context(self.mxnet_ctx)
        return reqs

    def postprocess(self, data):
        m = max(data)
        val = [i for i, j in enumerate(data) if j == m]
        return ["Prediction is {} with probability of {}%".format(val, m.asscalar()*100)]


_service = MXNetVisionServiceBatching()


def handle(data, context):
    if not _service.initialized:
        _service.initialize(context)

    if data is None:
        return None

    try:
        data = _service.preprocess(data)
        data = _service.inference(data)
        data = _service.postprocess(data)

        return data
    except Exception as e:
        logging.error(e, exc_info=True)
        raise


if __name__ == "__main__":
    f = open("utils/9.png", "rb")
    img = f.read()
    d_in = [{"data": img}]

    print(handle(d_in, None))
