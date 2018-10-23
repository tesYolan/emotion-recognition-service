#!/bin/bash
snet_daemon_v=0.1.0

# apt install tar
if [ ! -f snetd-linux-amd64 ]; then
	echo "Downloading snetd-linux"
	wget https://github.com/singnet/snet-daemon/releases/download/v0.1.0/snetd-$snet_daemon_v.tar.gz 

	tar -xvf snetd-$snet_daemon_v.tar.gz

	# May be should we define a cache.
	rm snetd-$snet_daemon_v.tar.gz
else
	echo "File seems to exist"
fi

python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. models/grpc/emotion_service.proto
