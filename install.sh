#!/bin/bash

snet_daemon_v=0.1.5

# apt install tar
if [ ! -d snetd-$snet_daemon_v ] ; then
	echo "Downloading snetd-linux"
	wget https://github.com/singnet/snet-daemon/releases/download/v$snet_daemon_v/snet-daemon-v$snet_daemon_v-linux-amd64.tar.gz
	tar -xzf snetd-$snet_daemon_v-linux-amd64.tar.gz -C snetd-$snet_daemon_v
	rm snetd-$snet_daemon_v-linux-amd64.tar.gz
else
	echo "Folder seems to exist"
fi

python3.6 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service_spec/EmotionService.proto

python3.6 get_models.py
