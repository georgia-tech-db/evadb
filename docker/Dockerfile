FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

ARG PYTHON_VERSION=3.8

# install system-wide package
RUN apt-get update \
    && apt-get -y install sudo wget bash openjdk-8-jdk openjdk-8-jre

# set eva user and no password sudo
RUN useradd -m eva && echo "eva:eva" | chpasswd && adduser eva sudo
RUN echo "eva ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER eva

# install miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && chmod +x ~/miniconda.sh \
    && bash ~/miniconda.sh -b -p ~/miniconda \
    && hash -r \
    && ~/miniconda/bin/conda config --set always_yes yes --set changeps1 no \
    && ~/miniconda/bin/conda update -q conda \
    && ~/miniconda/bin/conda info -a

COPY . /app
RUN sudo chown -R eva:eva /app

# install eva env
RUN ~/miniconda/bin/conda env create -f /app/script/install/conda_eva_environment.yml

# sanity check for GPU
RUN ~/miniconda/bin/conda run -n eva python -c "import torch; torch.randn(1).cuda()"

# generate eva-ql parser
RUN wget https://www.antlr.org/download/antlr-4.8-complete.jar -O ~/antlr.jar \
    && java -jar ~/antlr.jar -Dlanguage=Python3 /app/src/parser/evaql/evaql_lexer.g4 \
    && java -jar ~/antlr.jar -Dlanguage=Python3 -visitor /app/src/parser/evaql/evaql_parser.g4 \
    && rm ~/antlr.jar
