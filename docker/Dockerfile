FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu20.04 

WORKDIR /app
RUN chmod -R 777 /app

# Install python3.9
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      python3.9 \
      python3.9-distutils \
      curl \
      ffmpeg \
      && \
    apt-get autoremove --purge -y && \
    apt-get autoclean -y && \
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# Install pip
RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3.9 get-pip.py && \
    rm get-pip.py

# Create a non-root user and switch to it
RUN useradd -m evauser
USER evauser
ENV PATH="/home/evauser/.local/bin:${PATH}"

# Give Permission To Home Directory To Create EVA
RUN mkdir /home/evauser/.eva && chmod -R 777 /home/evauser/.eva
RUN mkdir /home/evauser/.cache && chmod -R 777 /home/evauser/.cache

# Install EVA
RUN python3.9 -m pip install evadb 

# EVA runs on port 8083
EXPOSE 8083

CMD ["eva_server"]