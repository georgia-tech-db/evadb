FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

ARG PYTHON_VERSION=3.8

# install system-wide package
RUN apt-get update && \
	apt-get -y install sudo wget

# set eva user
RUN useradd -m eva && echo "eva:eva" | chpasswd && adduser eva sudo
RUN echo "eva ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER eva

COPY . /app

RUN sh /app/script/install/before_install.sh
RUN sh /app/script/install/install.sh
