# EVA (Exploratory Video Analytics)

[![Build Status](https://travis-ci.org/georgia-tech-db/eva.svg?branch=master)](https://travis-ci.com/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/exvian/badge/?version=latest)](https://evagatech.readthedocs.io/en/latest/index.html) [![Join the chat at https://gitter.im/georgia-tech-db/eva](https://badges.gitter.im/georgia-tech-db/eva.svg)](https://gitter.im/georgia-tech-db/eva?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## What is EVA?

EVA is a visual data management system (think MySQL for videos). It supports a declarative language similar to SQL and a wide range of commonly used  computer vision models.

## What does EVA do?

* EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.

* EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

* EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

## Installation

### Dependency
EVA requires Python 3.7 or 3.8 and JAVA 8. On Ubuntu, you can install the JAVA by `sudo -E apt install -y openjdk-8-jdk openjdk-8-jre`.

### Recommended
To install EVA, we recommend using pip:
```shell
pip3 install evatestdb
```

## Verify Installation

1. Set up the server and client

- Launch EVA database Server: `eva_server`

- Launch CLI: `eva_client`

2. Run the `UPLOAD` command in the client terminal (use the [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) as an example):
```mysql
UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
```

3. Run the `LOAD` command in the client terminal: (may take a while)
```mysql
LOAD DATA INFILE 'test_video.mp4' INTO MyVideo;
```

4. Below is a basic query that should work on the client
```mysql
SELECT id, data FROM MyVideo WHERE id < 5;
```

### Troubleshoot

* PySpark's error: `java.io.IOException: Cannot run program "python":`. Set the Python location for Spark. For example, `export PYSPARK_PYTHON=/usr/bin/python3`. Then you need to clean the old DB and PySpark data by `rm ~/.eva/eva_catalog.db && rm -rf ~/.eva/eva_datasets`.

## Quickstart Tutorial

### Configure GPU (Recommended)

1. If your workstation has a GPU, you need to first set it up and configure it. You can run the following command first to check your hardware capabilities. 

    ```
    ubuntu-drivers devices
    ```

    If you do have an NVIDIA GPU, and its not been configured yet, follow all the steps in this link carefully. `https://towardsdatascience.com/deep-learning-gpu-installation-on-ubuntu-18-4-9b12230a1d31`. 

    Some pointers:
    - When installing NVIDIA drivers, check the correct driver version for your GPU to avoid compatibiility issues. 
    - When installing cuDNN, you will have to create an account. Make sure you get the correct deb files for your OS and architecture. 

2. You can run the following code in a jupyter instance to verify your GPU is working well along with PyTorch.

    ```
    import torch
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(device)
    ```

    Output of `cuda:0` indicates the presence of a GPU. (Note: 0 indicates the index of the GPU in system. Incase you have multiple GPUs, the index needs to be accordingly changed)

2. Now configure the `executor` section in `~/.eva/eva.yml` as follows:

    ```
    gpus: {'127.0.1.1': [0]}
    ```
    
    `127.0.1.1` is the loopback address on which the eva server is started. 0 refers to the GPU index to be used. 

### Sample Notebook

1. Open a terminal instance and start the server:
    ```
    eva_server
    ```

2. Open another terminal instance. Start a jupyter lab/notebook instance, and navigate to [tutorials/object_detection.ipynb](tutorials/object_detection.ipynb)

3. You might have to install ipywidgets to visualize the input video and output. Follow steps in `https://ipywidgets.readthedocs.io/en/latest/user_install.html` as per your jupyter environment. 

4. Run each cell one by one. Each cell is self-explanatory. If everything has been configured correctly you should be able to see a ipywidgets Video instance with the bounding boxes output of the executed query.

## Documentation

You can find documentation and code snippets for EVA [here](https://evagatech.readthedocs.io/).

## Contributing

To file a bug or request a feature, please file a GitHub issue. Pull requests are welcome.

For information on installing from source and contributing to EVA, see our
[contributing guidelines](./CONTRIBUTING.md).

## Contributors

See the [people page](https://github.com/georgia-tech-db/eva/graphs/contributors) for the full listing of contributors.

## License
Copyright (c) 2018-2020 [Georgia Tech Database Group](http://db.cc.gatech.edu/)
Licensed under the [Apache License](LICENSE).
