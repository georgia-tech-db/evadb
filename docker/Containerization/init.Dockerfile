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
RUN python3 -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# Get the repo and install the dev portion.
RUN git clone https://github.com/georgia-tech-db/eva.git
RUN cd eva && pip install -e ".[dev]"         

# run the eva EVA suite
# RUN cd eva && bash script/test/test.sh