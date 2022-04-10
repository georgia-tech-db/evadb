FROM ubuntu:18.04

ARG PYTHON_VERSION=3.7

# install system-wide package
RUN apt-get update \
    && apt-get -y install sudo wget bash openjdk-8-jdk \
    && apt-get -qq install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    yasm \
    pkg-config \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libavformat-dev \
    libpq-dev \
    && apt-get -y install gcc python-dev python3-dev python3-venv python3.7-dev python3.8-dev

# Give Permission To Home Directory
RUN mkdir /.eva && chmod -R 777 /.eva
