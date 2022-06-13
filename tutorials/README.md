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
