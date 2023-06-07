Getting Started
====

Step 1: Install EVA
----

EVA supports Python (versions >= 3.8). To install EVA, we recommend using the pip package manager:

.. code-block:: bash

    pip install evadb


Connect to EvaDB in your Python file
----

Grab a ``cursor`` to run AI pipelines using EvaDB.

.. code-block:: bash

    import evadb
    cursor = evadb.connect().cursor()

Part 2: Start a Jupyter Notebook Client
----

Here is an `illustrative Jupyter notebook <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html>`_ focusing on MNIST image classification using EVA. The notebook works on `Google Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/01-mnist.ipynb>`_. 

Connect to the EVA server
~~~~

Connect to the EVA server in the notebook using the following code:

.. code-block:: python

    # allow nested asyncio calls for client to connect with server
    import nest_asyncio
    nest_asyncio.apply()
    from evadb.server.db_api import connect

    # hostname and port of the server where EVA is running
    connection = connect(host = '0.0.0.0', port = 8803)

    # cursor allows the notebook client to send queries to the server
    cursor = connection.cursor()

Load video for analysis
~~~~

Download the MNIST video for analysis.

.. code-block:: bash

    !wget -nc https://www.dropbox.com/s/yxljxz6zxoqu54v/mnist.mp4

Use the LOAD statement to load a video onto a table in EVA server. 

.. code-block:: python

    cursor.execute('LOAD VIDEO "mnist.mp4" INTO MNISTVideoTable;')
    response = cursor.fetch_all()
    print(response)

Step 3: Run an AI Query on the loaded video
----

User-defined functions (UDFs) allow us to combine SQL with AI models. These functions wrap around AI models. In this query, we use the `MnistImageClassifier` UDF that wraps around a model trained for classifying `MNIST` images.

.. code-block:: python

    cursor.execute("""SELECT data, MnistImageClassifier(data).label 
                      FROM MNISTVideoTable
                      WHERE id = 30;""")
    response = cursor.fetch_all()

Visualize the output
~~~~

The output of the query is `visualized in the notebook <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html#visualize-output-of-query-on-the-video>`_.

.. image:: https://evadb.readthedocs.io/en/stable/_images/01-mnist_15_0.png
