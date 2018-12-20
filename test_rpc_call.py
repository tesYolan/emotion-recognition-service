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


class TestSuiteGrpc(unittest.TestCase):
    def setUp(self):
        with open('turtles.png', 'rb') as f:
            img = f.read()
            self.image_64 = base64.b64encode(img).decode('utf-8')
        # How to run python3.6 script.py script to
        self.port = "8001"
        self.server = script.create_server(self.port)
        self.server.start()
        self.result = ('predictions: "fear"\n'
                      'predictions: "happy"\n'
                      'predictions: "sad"\n'
                      'predictions: "happy"\n'
                      'predictions: "anger"\n'
                      'predictions: "happy"\n'
                      'bounding_boxes {\n'
                      '  x: 572\n'
                      '  y: 112\n'
                      '  w: 104\n'
                      '  h: 103\n'
                      '}\n'
                      'bounding_boxes {\n'
                      '  x: 841\n'
                      '  y: 161\n'
                      '  w: 150\n'
                      '  h: 150\n'
                      '}\n'
                      'bounding_boxes {\n'
                      '  x: 365\n'
                      '  y: 42\n'
                      '  w: 104\n'
                      '  h: 104\n'
                      '}\n'
                      'bounding_boxes {\n'
                      '  x: 411\n'
                      '  y: 286\n'
                      '  w: 124\n'
                      '  h: 125\n'
                      '}\n'
                      'bounding_boxes {\n'
                      '  x: 742\n'
                      '  y: 93\n'
                      '  w: 125\n'
                      '  h: 124\n'
                      '}\n'
                      'bounding_boxes {\n'
                      '  x: 145\n'
                      '  y: 112\n'
                      '  w: 149\n'
                      '  h: 149\n'
                      '}\n')

    def load_image(self):
        query = '{"image_type": "png", "image" : "' + str(self.image_64) + '"}'
        with open('query.json', 'wt') as f:
            f.write(str(query))

    def test_grpc_call(self):
        with grpc.insecure_channel('localhost:' + self.port) as channel:
            stub = EmotionRecognitionStub(channel)
            request = RecognizeRequest(image_type='png', image=self.image_64)
            feature = stub.classify(request)
            self.assertMultiLineEqual(self.result, str(feature), "GRPC Funtioning smootly for provided image.")

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
