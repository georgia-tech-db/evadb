# Contributing to EVA

## Setting up Development Environment

### Installation

Installation of EVA involves setting a virtual environment using [miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) and configuring git hooks.

1. Clone the repository
```shell
git clone https://github.com/georgia-tech-db/eva.git
```

2. Install the dependencies.
```shell
sh script/install/before_install.sh
export PATH="$HOME/miniconda/bin:$PATH"
sh script/install/install.sh
```

<!-- 4. Install `docker` and `docker-compose`.
Please refer to [official doc](https://docs.docker.com/engine/install/). -->

### Client Testing

1. Set up the server and client

- Activate the conda environment: `conda activate eva`

- Launch EVA database Server: `python eva/eva_server.py`

- Launch CLI: `python eva/eva_cmd_client.py`

2. Run the `UPLOAD` command in the client terminal:
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

2. Now configure the `executor` section in `eva.yml` as follows:

    ```
    gpus: {'127.0.1.1': [0]}
    ```
    
    `127.0.1.1` is the loopback address on which the eva server is started. 0 refers to the GPU index to be used. 

## Commiting and Testing

1. Install git hooks in your .git/ directory. [optional, but recommended]
```shell
conda activate eva
pre-commit install
```

2. Ensure that all the unit test cases (including the ones you have added) run succesfully and the coding style conventions are followed.
```shell
bash script/test/test.sh
```

## Packaging New Version of EVA

1. Generate EVA grammar files.
```shell
bash script/antlr4/generate_parser.sh
```

2. Bump up version number in `setup.cfg` along with any additional dependencies.

3. Create a new build locally.
```shell
python -m build
```

4. Upload build to pypi using credentials.
```shell
python -m twine upload dist/*
```


## Issues and PR's

To file a bug or request a feature, please file a GitHub issue. Pull requests are welcome.
