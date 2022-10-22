FROM python:3.8

## Usage
# docker build -t eva .
# docker run -it eva

RUN apt-get -qq update
RUN apt-get -qq install -y --no-install-recommends \
    openjdk-11-jdk \
    openjdk-11-jre

RUN mkdir /eva && chmod -R 777 /eva
ADD . /eva
WORKDIR eva

RUN script/antlr4/generate_parser.sh
RUN pip install -e ".[dev]"

RUN chmod +x ./docker-run.sh
CMD ./docker-run.sh
