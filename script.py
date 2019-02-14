import base64
import tempfile

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
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Image is required")
        if request.image_type is None:
            pass

        binary_image = base64.b64decode(request.image)
        bounding_boxes, emotions = self._classify(binary_image)
        response = RecognizeResponse()

        for d, e in zip(bounding_boxes, emotions):
            response.faces.add(bounding_box=BoundingBox(x=d.left(), y=d.top(), w=d.right() - d.left(), h=d.bottom() - d.top()),
                                  emotion=e)

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


def create_server(port=8001):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    add_EmotionRecognitionServicer_to_server(EmotionRecognitionServicer(), server)
    server.add_insecure_port('[::]:' + str(port))
    return server


if __name__ == '__main__':
    server = create_server()
    server.start()
    _ONE_DAY = 60*60*24
    try:
        while True:
            time.sleep(_ONE_DAY)
    except KeyboardInterrupt:
        server.stop(0)

