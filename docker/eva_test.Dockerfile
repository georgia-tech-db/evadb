FROM ubuntu:18.04

ARG PYTHON_VERSION=3.8

# install system-wide package
RUN apt-get update \
    && apt-get -y install sudo wget bash openjdk-8-jdk openjdk-8-jre \
    && apt-get -y install gcc python-dev python3-dev python3.7-dev python3.7-venv
