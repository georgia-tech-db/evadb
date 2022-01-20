.. _guide-tutorials:

Tutorials
=============

Configure GPU (Recommended)
----------------------------

1. If your workstation has a GPU, you need to first set it up and configure it. You can run the following command first to check your hardware capabilities.

    .. code-block:: bash

        ubuntu-drivers devices
        nvidia-smi

    A valid output from the commands indicates that your GPU is configured and ready to use. If not, you need to first install necessary drivers and configure your GPU. `this <https://towardsdatascience.com/deep-learning-gpu-installation-on-ubuntu-18-4-9b12230a1d31>`_ page provides a step-by-step guide to install and configure the drivers for ubuntu. 

    Some pointers:
        * When installing NVIDIA drivers, check the correct driver version for your GPU to avoid compatibiility issues.
        * When installing cuDNN, you will have to create an account. Make sure you get the correct deb files for your OS and architecture.

2. You can run the following code in a jupyter instance to verify your GPU is working well along with PyTorch.

    .. code-block:: python

        import torch
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        print(device)

    Output of `cuda:0` indicates the presence of a GPU. 
    (Note: 0 indicates the index of the GPU in system. Incase you have multiple GPUs, the index needs to be accordingly changed)

3. Now configure the executor section in eva.yml as follows:

    .. code-block:: yaml

        executor:
            
            gpus: {'127.0.1.1': [0]}

    `127.0.1.1` is the loopback address on which the eva server is started. 0 refers to the GPU index to be used.

Quickstart Notebook
--------------------

1. Start server:

    Open a terminal instance and start the server:
    .. code-block:: bash

        python eva.py

2. Start client:

    * Open another terminal instance. Start a jupyter lab/notebook instance, and navigate to `tutorials/object_detection.ipynb`. 
    
    * You might have to install ipywidgets to visualize the input video and output. Follow steps `here <https://ipywidgets.readthedocs.io/en/latest/user_install.html>`_ as per your jupyter environment.

3. Run cells:

    * Each cell is self-explanatory. If everything has been configured correctly you should be able to see a ipywidgets Video instance with the bounding boxes output of the executed query.



