# https://www.jenkins.io/doc/book/installing/docker/ - Follow these steps for starting jenkins.
# FROM nvidia/cuda:11.6.2-cudnn8-runtime-ubuntu20.04

# Docker image specific installation
# RUN apt-get update && \
#     DEBIAN_FRONTEND=noninteractive apt-get install -y \
#       python3-numpy \
#       python3-pip \
#       python3-pytest \
#       python3-pytest-cov \
#       python3-venv \
#       python3-yaml \
#       ffmpeg \
#       && \
#     apt-get autoremove --purge -y && \
#     apt-get autoclean -y && \
#     rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# OpenCV Specific Installation
# RUN apt-get -qq update && \
#     apt-get -qq install -y --no-install-recommends \
#         build-essential \
#         cmake \
#         git \
#         wget \
#         unzip \
#         yasm \
#         pkg-config \
#         ffmpeg \
#         libsm6 \
#         libxext6 \
#         libswscale-dev \
#         libtbb2 \
#         libtbb-dev \
#         libjpeg-dev \
#         libpng-dev \
#         libtiff-dev \
#         libopenjp2-7-dev \
#         libavformat-dev \
#         libpq-dev \
#         python3-dev \
#         sudo \
#         openjdk-11-jdk \
#         openjdk-11-jre


# RUN pip install evadb
# RUN eva_server&

# Base
FROM ubuntu:latest

# General requirements
RUN apt-get update
RUN apt-get install git -y
RUN apt-get install build-essential -y
RUN apt-get install cmake -y
RUN apt-get install wget -y
RUN apt-get install unzip -y
RUN apt-get install sudo -y
RUN apt-get install python3 -y
RUN apt-get install python3-numpy -y
RUN apt-get install python3-pip -y
RUN apt-get install python3-venv -y
RUN apt-get install python3-pytest -y

# Get the eva db and run it's test, then run the server.
RUN git clone https://github.com/georgia-tech-db/eva.git
RUN cd eva

# create a virtual environment
RUN python3 -m venv test_eva_db       

# activate the virtual environment, using "." instead of "source" to specify from bash.
RUN . test_eva_db/bin/activate   

# upgrade pip
RUN pip install --upgrade pip         

# build and install the EVA package
# RUN pip install -e ".[dev]"           

# run the eva EVA suite
# RUN bash script/test/test.sh          

# RUN pkill -9 eva_server   # kill running EVA server (if any)
# RUN eva_server&           # launch EVA server with newly installed package