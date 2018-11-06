import jsonrpcclient
import base64

import grpc
from service_spec.EmotionService_pb2_grpc import EmotionRecognitionStub
from service_spec.EmotionService_pb2 import RecognizeResponse, BoundingBox, RecognizeRequest
import subprocess
import sys
import argparse
import time
import yaml

with open('turtles.png', 'rb') as f:
    img = f.read()
    image_64 = base64.b64encode(img).decode('utf-8')

def test_grpc_call(port):
    with grpc.insecure_channel('localhost:' + port) as channel:
         stub = EmotionRecognitionStub(channel)
         request = RecognizeRequest(image_type='png', image=image_64)
         feature = stub.classify(request)
         print(feature)

def test_deployed_service(job_address):
    query = '{"image_type": "png", "image" : "' + str(image_64) + '"}'
    with open('query2.json', 'wt') as f:
        f.write(str(query))

    p = subprocess.Popen(["snet", "--print-traceback", "client", "call", "--agent-at", "0x7fE17B093E13379247336DDD846deF8624Ae8a9C", "--job-at", job_address, "classify", "query2.json","-y"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result, err = p.communicate()
    print(result)
    print(err)

    preprocessed_results = yaml.load(result)['response']
    print(preprocessed_results)

    return preprocessed_results

def test_deployed_service(job_address):
    query = '{"image_type": "png", "image" : "' + str(image_64) + '"}'
    with open('query2.json', 'wt') as f:
        f.write(str(query))

    p = subprocess.Popen(["snet", "--print-traceback", "client", "call", "--agent-at", "0x7fE17B093E13379247336DDD846deF8624Ae8a9C", "classify", "query2.json","-y"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result, err = p.communicate()
    print(result)
    print(err)

    preprocessed_results = yaml.load(result)['response']
    print(preprocessed_results)

    return preprocessed_results

def test_call():
    query = '{"image_type": "png", "image" : "' + str(image_64) + '"}'
    with open('query2.json', 'wt') as f:
        f.write(str(query))

    p = subprocess.Popen(["snet", "client", "call", "--agent-at", "0x7fE17B093E13379247336DDD846deF8624Ae8a9C", "classify", "query2.json","-y"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result, err = p.communicate()
    print(result)
    print(err)

    preprocessed_results = yaml.load(result)['response']
    print(preprocessed_results)

    return preprocessed_results

parser = argparse.ArgumentParser(prog="test")

parser.add_argument("--test_grpc", help="test grpc at given port")
parser.add_argument("--test_with_job", help="given a job test the service for action")
parser.add_argument("--test", help="given a job test the service for action")
args = parser.parse_args(sys.argv[1:])

if args.test_grpc is not None:
    test_grpc_call(args.test_grpc)

if args.test_with_job is not None:
    test_deployed_service(args.test_with_job)

if args.test is not None:
    test_call()
