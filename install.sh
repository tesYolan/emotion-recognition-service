#!/bin/bash

snet_daemon_v=0.1.3

# apt install tar
if [ ! -d snetd-$snet_daemon_v ] ; then
	echo "Downloading snetd-linux"
	wget https://github.com/singnet/snet-daemon/releases/download/v$snet_daemon_v/snetd-$snet_daemon_v.tar.gz

	y=`uname`
	if [ $y == "Darwin" ]; then
		echo "MacOS creates folder"
		mkdir snetd-$snet_daemon_v
	else
		echo "Using linux, tar creates a folder by itself"
	fi
	tar -xzf snetd-$snet_daemon_v.tar.gz -C snetd-$snet_daemon_v

	# May be should we define a cache.
	rm snetd-$snet_daemon_v.tar.gz
else
	echo "Folder seems to exist"
fi

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service_spec/EmotionService.proto

python get_models.py
