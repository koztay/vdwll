#!/bin/bash

xhost +local:
docker run -d \
     --env="DISPLAY" \
     --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
     plumbee/nvidia-virtualgl \
sh -c 'apt-get update && apt-get install -qqy firefox && vglrun firefox'
