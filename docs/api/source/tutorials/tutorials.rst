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

Quickstart Tutorial
--------------------

1. **Start server**:

    * Open a terminal instance and start the server:

        .. code-block:: bash

            python eva.py

2. **Start client**:

    * Open another terminal instance. Start a jupyter lab/notebook instance, and navigate to `tutorials/object_detection.ipynb`.

    * You might have to install ipywidgets to visualize the input video and output. Follow steps `here <https://ipywidgets.readthedocs.io/en/latest/user_install.html>`_ as per your jupyter environment.

3. **Notebook walkthrough**:

    * Establish connection with the DB:

        .. code-block:: python

            import nest_asyncio
            nest_asyncio.apply()
            connection = connect(host = '0.0.0.0', port = 5432)
            cursor = connection.cursor()

        We use `nest_asyncio` to allow nested asyncio calls. This is required for the client to work with the server. `cursor` is a cursor object that allows us to execute queries on the database.

    * Upload a video to be analyzed:

        .. code-block:: python

            cursor.execute('UPLOAD INFILE "../data/ua_detrac/ua_detrac.mp4" PATH "video.mp4";')
            response = cursor.fetch_all()
            print(response)

        The `UPLOAD` command is used to upload a video to EVA. `INFILE` takes in the path of the video on filesystem and `PATH` is the path where the video is to be stored in the database.

    * Visualize video:

        .. code-block:: python

            from ipywidgets import Video
            Video.from_file("../data/ua_detrac/ua_detrac.mp4", embed=True)

    * Load the video into EVA:

        .. code-block:: python

            cursor.execute('LOAD DATA INFILE "video.mp4" INTO MyVideo;')
            response = cursor.fetch_all()
            print(response)

        The 'LOAD' command is used to load a video into EVA. `INFILE` is the path of the video in the database.

    * Registering UDFs (User Defined Functions):

        .. code-block:: python

            cursor.execute("""CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
                INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                            scores NDARRAY FLOAT32(ANYDIM))
                TYPE  Classification
                IMPL  'src/udfs/fastrcnn_object_detector.py';
                """)
            response = cursor.fetch_all()
            print(response)

        To learn more about UDFs, refer to `this <udf.html>`_.

    * Run the UDF:

        .. code-block:: python

            cursor.execute("""SELECT id, Unnest(FastRCNNObjectDetector(data)) FROM MyVideo""")
            response = cursor.fetch_all()

        UDFs are typically used like sql functions along with the 'SELECT' command. The 'Unnest' function is used to unnest the output of the UDF.

    Shown above is a quickstart tutorial of how you can use EVA for your video analysis tasks.
