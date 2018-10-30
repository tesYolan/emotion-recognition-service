FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        python3.6 \
        python3.6-dev \
        python3-pip \
        python-setuptools \
        cmake \
        wget \
        curl \
        libsm6 \
        libxext6 \ 
        libxrender-dev

COPY requirements-docker-gpu.txt /tmp

WORKDIR /tmp

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6
RUN python3.6 -m pip install -r requirements-docker-gpu.txt

COPY . /emotion-recognition-service

WORKDIR /emotion-recognition-service

# EXPOSES the port where jsonrpc is being heard.
EXPOSE 8001
EXPOSE 6005

RUN python3.6 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service_spec/EmotionService.proto

CMD ['python3.6', 'run-snet-service.py', "--daemon-config", "snetd.json"]
