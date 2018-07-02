FROM debian:jessie-slim

RUN apt-get update
RUN apt-get -y install emacs24

RUN useradd -G sudo -u 1000 --create-home emacs

ENV HOME /home/emacs
WORKDIR /home/emacs

CMD /usr/bin/emacs --reverse
