# https://www.jenkins.io/doc/book/installing/docker/ - Follow these steps for starting jenkins.
FROM nvidia/cuda:11.3.0-cudnn8-runtime-ubuntu20.04

# Install Python
RUN apt-get -qq update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt install -y python3.8 python3.8-venv python3-pip \
    && python3 -m pip install --upgrade pip

RUN apt install -y openjdk-11-jdk openjdk-11-jre wget
RUN mkdir /eva && chmod -R 777 /eva && mkdir /src
COPY ./ /src

WORKDIR /src
RUN chmod -R 777 /src \
    && sh script/antlr4/generate_parser.sh \
    && pip install -e ".[dev]"

WORKDIR /eva
