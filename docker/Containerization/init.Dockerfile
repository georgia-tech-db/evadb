# FROM ubuntu:latest
 
# RUN apt-get -y update
# RUN apt-get -y upgrade
# RUN apt-get install -y build-essential

# https://www.jenkins.io/doc/book/installing/docker/ - Follow these steps for starting jenkins.
FROM nvidia/cuda:11.6.2-cudnn8-runtime-ubuntu20.04

# Docker image specific installation
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      python3-numpy \
      python3-pip \
      python3-pytest \
      python3-pytest-cov \
      python3-venv \
      python3-yaml \
      ffmpeg \
      && \
    apt-get autoremove --purge -y && \
    apt-get autoclean -y && \
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# OpenCV Specific Installation
RUN apt-get -qq update && \
    apt-get -qq install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        ffmpeg \
        libsm6 \
        libxext6 \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libopenjp2-7-dev \
        libavformat-dev \
        libpq-dev \
        python3-dev \
        sudo \
        openjdk-11-jdk \
        openjdk-11-jre

# RUN pip install evadb
# RUN eva_server &

# Get the eva db and run it's test, then run the server.
RUN git clone https://github.com/georgia-tech-db/eva.git && cd eva
RUN python3 -m venv test_eva_db       # create a virtual environment
RUN source test_eva_db/bin/activate   # activate the virtual environment
RUN pip install --upgrade pip         # upgrade pip
RUN pip install -e ".[dev]"           # build and install the EVA package
RUN bash script/test/test.sh          # run the eva EVA suite

RUN pkill -9 eva_server   # kill running EVA server (if any)
RUN eva_server&           # launch EVA server with newly installed package