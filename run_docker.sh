#!/usr/bin/env bash
docker build -f Dockerfile.gpu -t singularitynet/emotion-recognition-service .
docker run -v /etc/letsencrypt:/etc/letsencrypt --runtime=nvidia --name emotion-recognition-service -p 6305:6305 -p 6205:6205 -d -it singularitynet/emotion-recognition-service:latest