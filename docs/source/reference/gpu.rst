:orphan:

Configure GPU 
-------------

1. Queries in EvaDB use deep learning models that run much faster on a GPU as opposed to a CPU. If your workstation has a GPU, you can configure EvaDB to use the GPU during query execution. Use  the following command to check your hardware capabilities:

.. code-block:: bash

    ubuntu-drivers devices
    nvidia-smi

A valid output from the command indicates that your GPU is configured and ready to use. If not, you will need to install the appropriate GPU driver. `This page <https://towardsdatascience.com/deep-learning-gpu-installation-on-ubuntu-18-4-9b12230a1d31>`_ provides a step-by-step guide on installing and configuring the GPU driver in the Ubuntu Operating System.

    * When installing an NVIDIA driver, ensure that the version of the GPU driver is correct to avoid compatibility issues.
    * When installing cuDNN, you will need to create an account and ensure that you get the correct `deb` files for your operating system and architecture.

2. You can run the following code in a Jupyter notebook to verify that your GPU is detected by PyTorch:

.. code-block:: python

    import torch
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(device)

Output of `cuda:0` indicates the presence of a GPU. 0 indicates the index of the GPU in system. If you have multiple GPUs on your workstation, the index must be updated accordingly.

3. Now configure the executor section in evadb.yml as follows:

.. code-block:: yaml

    executor:
        gpus: {'127.0.1.1': [0]}

Here, `127.0.1.1` is the loopback address on which the EvaDB server is running. 0 refers to the GPU index to be used.
