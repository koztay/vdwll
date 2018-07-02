#!/usr/bin/env bash

# rsync -a [/local/path/] [user@host]:[remote/path/]

#rsync . karnas-probook@10.0.0.100:/home/karnas-probook/Developer/

rsync -chavzP --stats . karnas-probook@10.0.0.100:/home/karnas-probook/Developer/

# yukarıdakilerin hepsi çalışıyor...
# /Users/kemal/WorkSpace/Videowall Development/media/pixar.mp4
# /Users/kemal/WorkSpace/Videowall Development/media/si_se_the_truth.mp3

# /home/karnas-probook/Developer/media/pixar.mp4