import base64
import random
import os
import tempfile
import json
from multiprocessing import Pool

from aiohttp import web
from jsonrpcserver.aio import methods
from jsonrpcserver.exceptions import InvalidParams

import grpc
import time
from concurrent import futures
from demo import load_model_from_args, start_image_demo
from service_spec.EmotionService_pb2 import RecognizeResponse, BoundingBox
from service_spec.EmotionService_pb2_grpc import EmotionRecognitionServicer, add_EmotionRecognitionServicer_to_server


class Args:
    """
    With this class, we call the function to load the model
    """
    def __init__(self):
        self.json = 'models/models/model-ff.json'
        self.weights = 'models/models/model-ff.h5'
        self.model_input = 'image'
        # TODO currenty we save, so this should be set this False for now
        self.snet = False
        self.gui = False
        self.path = ''
        self.image = ''


class Model:
    def __init__(self):
        self.args = Args()
        self.model = load_model_from_args(self.args)

    def predict(self):
        return start_image_demo(self.args, self.model)

class EmotionRecognitionServicer(EmotionRecognitionServicer):
    def classify(self, request, context):
        if request.image is None:
            raise InvalidParams("Image is required")
        if request.image_type is None:
            raise InvalidParams("Image type is required")
        image = request.image
        binary_image = base64.b64decode(request.image)

        bounding_boxes, emotions = self._classify(binary_image)

        response = RecognizeResponse()

        for d in bounding_boxes:
            response.bounding_boxes.add(x=d.left(), y=d.top(), w=d.right() - d.left(), h=d.bottom() - d.top())
        # values = [ dict(x=d.left(), y=d.top(), w=d.right() - d.left(), h=d.bottom() - d.top()) for d in bounding_boxes ]
        response.predictions[:] = emotions

        return response
    def _classify(self, image):
        import tensorflow as tf
        from keras import backend as K
        tf_config = tf.ConfigProto()
        tf_config.gpu_options.allow_growth = True
        sess = tf.Session(config=tf_config)
        K.set_session(sess)

        model = Model()

        # Requires us to save the file to disk
        f = tempfile.NamedTemporaryFile()
        f.write(image)
        #f.close()
        # close vs. flush because flush apparently won't work on windows
        model.args.path = f.name
        print(f.name)
        bounding_boxes, emotions = model.predict()
        #os.unlink(f.name) # cleanup temp file

        del model
        sess.close()
        return bounding_boxes, emotions

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    add_EmotionRecognitionServicer_to_server(EmotionRecognitionServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    _ONE_DAY = 60*60*24
    try: 
        while True:
            time.sleep(_ONE_DAY)
    except KeyboardInterrupt:
        server.stop(0)


# app = web.Application()


# @methods.add
# async def classify(**kwargs):
#     image = kwargs.get("image", None)
#     image_type = kwargs.get("image_type", None)
#     if image is None:
#         raise InvalidParams("image is required")
#     if image_type is None:
#         raise InvalidParams("image type is required")
# 
#     binary_image = base64.b64decode(image)
# 
#     with Pool(1) as p:
#         bounding_boxes, emotions = p.apply(_classify, (binary_image,))
# 
#     return {
#         "bounding boxes": [
#             dict(x=d.left(), y=d.top(), w=d.right() - d.left(), h=d.bottom() - d.top()) for d in bounding_boxes
#         ],
#         "predictions": emotions
#     }
# 
# 
# async def handle(request):
#     request = await request.text()
#     response = await methods.dispatch(request, trim_log_values=True)
# 
#     if response.is_notification:
#         return web.Response()
#     else:
#         return web.json_response(response, status=response.http_status)


if __name__ == '__main__':
    # app.router.add_post('/', handle)
    # web.run_app(app, host="127.0.0.1", port=8001)
    serve()
