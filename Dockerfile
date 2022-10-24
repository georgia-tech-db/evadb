FROM python:3.8

## Usage
# docker build -t eva .
# docker run -it eva

RUN apt-get -qq update
RUN apt-get -qq install -y --no-install-recommends \
    openjdk-11-jdk \
    openjdk-11-jre

RUN mkdir /eva && chmod -R 777 /eva
ADD requirements.txt /eva
WORKDIR eva

RUN pip install -r requirements.txt
ADD . /eva
RUN pip install -e ".[dev]"

RUN script/antlr4/generate_parser.sh

RUN chmod +x ./docker-run.sh
CMD ./docker-run.sh
