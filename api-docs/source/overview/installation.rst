.. _guide-getstarted:

Getting Started
====

Part 1: Install EVA
----

EVA supports Python (versions >= 3.7). To install EVA, we recommend using the pip package manager:

.. code-block:: bash

    pip install evadb


Launch EVA server
----

EVA is based on a `client-server architecture <https://www.postgresql.org/docs/15/tutorial-arch.html>`_. To launch the EVA server, run the following command on the terminal:

.. code-block:: bash

    eva_server &

Part 2: Start a Jupyter Notebook Client
----

Here is an `illustrative Jupyter notebook <https://evadb.readthedocs.io/en/latest/source/tutorials/01-mnist.html>`_ focusing on MNIST image classification using EVA. The notebook works on `Google Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/01-mnist.ipynb>`_. 

Connect to the EVA server
~~~~

To connect to the EVA server in the notebook, use the following Python code:

.. code-block:: python

    # allow nested asyncio calls for client to connect with server
    import nest_asyncio
    nest_asyncio.apply()

    # hostname and port of the server where EVA is running
    connection = connect(host = '0.0.0.0', port = 5432)

    # cursor allows the notebook client to send queries to the server
    cursor = connection.cursor()

Load video for analysis
~~~~

Download the MNIST video.

.. code-block:: bash

    !wget -nc https://www.dropbox.com/s/yxljxz6zxoqu54v/mnist.mp4

Use the LOAD statement is used to load a video onto the EVA server. 

.. code-block:: python

    cursor.execute('LOAD FILE "mnist.mp4" INTO MNISTVid;')
    response = cursor.fetch_all()
    print(response)

Run a query
~~~~

Run a query over the video to retrieve the output of the MNIST CNN function that is included in EVA as a built-in user-defined function (UDF).

.. code-block:: python

    cursor.execute("""SELECT id, MnistCNN(data).label 
                    FROM MNISTVid 
                    WHERE id < 5;""")
    response = cursor.fetch_all()
    print(response)

That's it! You can now run more complex queries.

Part 3: Register an user-defined function (UDF)
----

User-defined functions allow us to combine SQL with deep learning models. These functions can wrap around deep learning models. 

Download an user-defined function for classifying MNIST images.

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/eva/master/tutorials/apps/mnist/eva_mnist_udf.py

.. code-block:: python

    cursor.execute("""CREATE UDF IF NOT EXISTS MnistCNN
                        INPUT  (data NDARRAY (3, 28, 28))
                        OUTPUT (label TEXT(2))
                        TYPE  Classification
                        IMPL  'eva_mnist_udf.py';
                    """)
    response = cursor.fetch_all()
    print(response)

Run a more interesting query using the newly registered UDF
~~~~

.. code-block:: python

    cursor.execute("""SELECT data, MnistCNN(data).label 
                        FROM MNISTVid
                        WHERE id = 30;""")
    response = cursor.fetch_all()

Visualize the Output
~~~~

The output of the query is `visualized in the notebook <https://evadb.readthedocs.io/en/latest/source/tutorials/01-mnist.html#visualize-output-of-query-on-the-video>`_.


Part 5: Start a Command Line Client
----

Besides the notebook interface, EVA also exports a command line interface for querying the server. This interface allows for quick querying from the terminal:

.. code-block:: bash

    >>> eva_client
    eva=# LOAD FILE "mnist.mp4" INTO MNISTVid;
    @status: ResponseStatus.SUCCESS
    @batch:

    0 Video successfully added at location: mnist.p4
    @query_time: 0.045

    eva=# SELECT id, data FROM MNISTVid WHERE id < 1000;
    @status: ResponseStatus.SUCCESS
    @batch:
                mnistvid.id     mnistvid.data 
        0          0           [[[ 0 2 0]\n [0 0 0]\n...         
        1          1           [[[ 2 2 0]\n [1 1 0]\n...         
        2          2           [[[ 2 2 0]\n [1 2 2]\n...         
        ..       ...
        997        997           [[[ 0 2 0]\n [0 0 0]\n...         
        998        998           [[[ 0 2 0]\n [0 0 0]\n...         
        999        999           [[[ 2 2 0]\n [1 1 0]\n...         

    [1000 rows x 2 columns]
    @query_time: 0.216  

    eva=# exit