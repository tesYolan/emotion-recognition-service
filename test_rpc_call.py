import base64
import grpc
import subprocess
import sys
import argparse
import time
import yaml
import script
import unittest
import difflib

from service_spec.EmotionService_pb2_grpc import EmotionRecognitionStub
from service_spec.EmotionService_pb2 import RecognizeResponse, BoundingBox, RecognizeRequest
from google.protobuf.json_format import MessageToJson, MessageToDict


class TestSuiteGrpc(unittest.TestCase):
    def setUp(self):
        with open('turtles.png', 'rb') as f:
            img = f.read()
            self.image_64 = base64.b64encode(img).decode('utf-8')
        # How to run python3.6 script.py script to
        self.port = "8001"
        self.server = script.create_server(self.port)
        self.server.start()

        self.result = {'faces': [{'emotion': 'fear', 'boundingBox': {'x': 572, 'y': 112, 'w': 104, 'h': 103}},
                                 {'emotion': 'happy', 'boundingBox': {'x': 841, 'y': 161, 'w': 150, 'h': 150}},
                                 {'emotion': 'sad', 'boundingBox': {'x': 365, 'y': 42, 'w': 104, 'h': 104}},
                                 {'emotion': 'happy', 'boundingBox': {'x': 411, 'y': 286, 'w': 124, 'h': 125}},
                                 {'emotion': 'anger', 'boundingBox': {'x': 742, 'y': 93, 'w': 125, 'h': 124}},
                                 {'emotion': 'happy', 'boundingBox': {'x': 145, 'y': 112, 'w': 149, 'h': 149}}]}

    def load_image(self):
        query = '{"image_type": "png", "image" : "' + str(self.image_64) + '"}'
        with open('query.json', 'wt') as f:
            f.write(str(query))

    def test_grpc_call(self):
        with grpc.insecure_channel('localhost:' + self.port) as channel:
            stub = EmotionRecognitionStub(channel)
            request = RecognizeRequest(image_type='png', image=self.image_64)
            feature = stub.classify(request)
            self.assertMultiLineEqual(str(self.result), str(MessageToDict(feature)), "GRPC Funtioning smootly for provided image.")

    def tearDown(self):
        self.server.stop(0)


class TestSuiteDeployed(unittest.TestCase):
    def setUp(self):
        with open('turtles.png', 'rb') as f:
            img = f.read()
            self.image_64 = base64.b64encode(img).decode('utf-8')

    def test_deployed_service(self, job_address):
        p = subprocess.Popen(
            ["snet", "--print-traceback", "client", "call", "--agent-at", "0x7fE17B093E13379247336DDD846deF8624Ae8a9C",
             "--job-at", job_address, "classify", "query.json", "-y"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        result, err = p.communicate()
        print(result)
        print(err)

        preprocessed_results = yaml.load(result)['response']
        print(preprocessed_results)

        return preprocessed_results

    def test_deployed_service(self, job_address):
        p = subprocess.Popen(
            ["snet", "--print-traceback", "client", "call", "--agent-at", "0x7fE17B093E13379247336DDD846deF8624Ae8a9C",
             "classify", "query.json", "-y"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result, err = p.communicate()
        print(result)
        print(err)

        preprocessed_results = yaml.load(result)['response']
        print(preprocessed_results)

        return preprocessed_results

    def test_call(self):
        p = subprocess.Popen(
            ["snet", "client", "call", "--agent-at", "0x7fE17B093E13379247336DDD846deF8624Ae8a9C", "classify",
             "query.json", "-y"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result, err = p.communicate()
        print(result)
        print(err)

        preprocessed_results = yaml.load(result)['response']
        print(preprocessed_results)

        return preprocessed_results

    def test_mpe_call(self):
        p = subprocess.Popen(
            ["snet", "mpe-client", "call_server", "0x38506005d6b25386aac998448ae5eb48f87f4277", "0", "10",
             "34.216.72.29:6205", "EmotionRecognition", "classify", "query.json"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, err = p.communicate()
        print(result)
        results = str(result)
        print(err)

        preprocessed_emotions = results[results.find('predictions'):results.find('bounding_boxes')].replace(
            'predictions: ', '').split("\\n")
        print(preprocessed_emotions)
        emotions = []
        for emotion in preprocessed_emotions:
            p_emotion = emotion.replace('"', '')
            if p_emotion != '':
                emotions.append(p_emotion)

        print(emotions)

        return emotions

    def tearDown(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(TestSuiteGrpc("test_grpc_call"))

    # suite.addTest(TestSuiteDeployed("test_deployed_service"))

    # suite.addTest(TestSuiteDeployed("test_mpe_call"))
    unittest.main()
