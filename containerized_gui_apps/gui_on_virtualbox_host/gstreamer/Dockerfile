FROM debian:8
MAINTAINER Kemal ÖZTAY <koztay@me.com>

RUN apt-get update && apt-get install -y  \
    autoconf \
    automake \
    bzip2 \
    g++ \
    git \
    gstreamer1.0-plugins-good \
    gstreamer1.0-tools \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-ugly  \
    libatlas3-base \
    libgstreamer1.0-dev \
    libtool-bin \
    make \
    python2.7 \
    python3 \
    python-pip \
    python-yaml \
    python-simplejson \
    python-gi \
    gir1.2-gtk-3.0 \
    subversion \
    wget \
    zlib1g-dev && \
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    pip install ws4py==0.3.2 && \
    pip install tornado && \    
    ln -s /usr/bin/python2.7 /usr/bin/python ; ln -s -f bash /bin/sh


COPY . /opt

WORKDIR /opt

RUN chmod +x /opt/start.sh && \
    chmod +x /opt/stop.sh && \
    chmod +x /opt/play.sh && \
    chmod +x /opt/entrypoint.sh
