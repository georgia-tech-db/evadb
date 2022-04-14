FROM ubuntu:18.04

ARG PYTHON_VERSION=3.8
ARG DEBIAN_FRONTEND=noninteractive

ENV OPENCV_VERSION="4.5.1"

# Setup Ubuntu
RUN apt-get update

# Install System Essentials
RUN apt-get -qq install -y --no-install-recommends \
    build-essential \
    sudo \
    wget \
    cmake \
    base \
    unzip \
    gcc \
    g++ \
    software-properties-common

# Install Python Necessary Stuff
RUN apt-get -qq install -y --no-install-recommends \
    python3-venv \
    python3.7-venv \
    python3.7-dev

# Download OpenCV From Version
RUN wget https://github.com/opencv/opencv/archive/4.5.1.zip \
    && unzip 4.5.1.zip \
    && cd opencv-4.5.1 \
    && mkdir release \
    && cd release \
    && cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON .. \
    && make \
    && make install

# Add Jenkins user
RUN groupadd --gid 1000 jenkins && \
    useradd --uid 1000 --gid jenkins --shell /bin/bash --home-dir /var/jenkins_home jenkins && \
    mkdir /var/jenkins_home && \
    chown 1000:1000 /var/jenkins_home && \
    echo 'jenkins ALL=NOPASSWD: ALL' >> /etc/sudoers.d/50-jenkins && \
    echo 'Defaults    env_keep += "DEBIAN_FRONTEND"' >> /etc/sudoers.d/env_keep

# Give Permission To Home Directory
RUN mkdir /.eva && chmod -R 777 /.eva
