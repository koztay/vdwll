#!/bin/bash

xhost +local:
docker run -it --rm \
       -v /tmp/.X11-unix:/tmp/.X11-unix \
       -v $HOME:/home/emacs/host_home \
       -e DISPLAY=$DISPLAY \
       --user 1000 \
       plumbee/nvidia-virtualgl \
       sh -c 'apt-get update && apt-get install -qqy firefox && vglrun firefox'

xhost -local: