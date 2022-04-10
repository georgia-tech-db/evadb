FROM ubuntu:16.04

ARG PYTHON_VERSION=3.8
ARG DEBIAN_FRONTEND=noninteractive

ENV OPENCV_VERSION="4.5.1"

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
    && apt-get -y install gcc python3-venv python3.7-venv python3.7-dev python3.8-dev python3-opencv

# Give Permission To Home Directory
RUN mkdir /.eva && chmod -R 777 /.eva
