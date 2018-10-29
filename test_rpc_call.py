import base64
import cv2

import grpc
from service_spec.EmotionService_pb2 import RecognizeResponse, BoundingBox, RecognizeRequest
from service_spec.EmotionService_pb2_grpc import EmotionRecognitionStub

with open('turtles.png', 'rb') as f:
        img = f.read()
        image_64 = base64.b64encode(img).decode('utf-8')

if __name__ == '__main__':
    # jsonrpcclient.request("http://127.0.0.1:{}".format(8001), "classify",image=image_64, image_type='png')
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = EmotionRecognitionStub(channel)
        request = RecognizeRequest(image_type='png', image=image_64)
        feature = stub.classify(request)
        print(feature)
