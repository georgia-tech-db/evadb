# https://www.jenkins.io/doc/book/installing/docker/ - Follow these steps for starting jenkins.
FROM nvidia/cuda:11.2.2-devel-ubuntu20.04

ENV OPENCV_VERSION="4.5.1"

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

# Give Permission To Home Directory To Create EVA
RUN mkdir /.eva && chmod -R 777 /.eva
RUN mkdir /.cache && chmod -R 777 /.cache
RUN mkdir /.EasyOCR && chmod -R 777 /.EasyOCR