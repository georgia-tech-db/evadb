FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu20.04 

# Set working directory
WORKDIR /app

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

# Install gcc and python3.9-dev
RUN apt-get update && apt-get install -y \
    gcc \
    python3.9-dev
    
# Install pip
RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3.9 get-pip.py && \
    rm get-pip.py

# Create a non-root user and switch to it
RUN useradd -m evauser 
RUN chown -R evauser:evauser /app
USER evauser
ENV PATH="/home/evauser/.local/bin:${PATH}"

# Install EvaDB
RUN python3.9 -m pip install evadb 

# Expose the default port EvaDB runs on 
EXPOSE 8803

# Start EvaDB server
CMD ["evadb_server"]