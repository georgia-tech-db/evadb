.. _Getting Started:

Getting Started
=================

Install EvaDB 
-------------

To install EvaDB, we recommend using the `pip` package manager.

1. Create a new `virtual environment <https://docs.python-guide.org
/dev/virtualenvs/>`_ called `evadb-venv`.

.. code-block:: bash

    python -m venv evadb-venv

Now, activate the virtual environment:

.. code-block:: bash

    source evadb-venv/bin/activate

2. Once inside the virtual environment, run the command below to mitigate the dependency issues.

.. code-block:: bash

   pip install --upgrade pip setuptools wheel

3. Install EvaDB

.. code-block:: bash

   pip install evadb

4. Verify EvaDB installation

.. code-block:: bash

   pip freeze

You should see a list of installed packages including but not limited to the following:

.. code-block:: bash
   Package           Version
   ----------------- -------
   aenum             3.1.15
   decorator         5.1.1
   diskcache         5.6.3
   evadb             0.3.3
   greenlet          2.0.2
   lark              1.1.7
   numpy             1.25.2
   pandas            2.1.0
   ...

5. Run EvaDB

Copy the following Python program to a file called `run_evadb.py`.

The program runs a SQL query for listing all the built-in functions in EvaDB. It consists of importing and connecting to EvaDB, and then running the query. The query's result is returned as a Dataframe.

.. code-block:: python

   # Import the EvaDB package 
   import evadb

   # Connect to EvaDB and get a database cursor for running queries
   cursor = evadb.connect().cursor()

   # List all the built-in functions in EvaDB
   print(cursor.query("SHOW UDFS;").df())

Now, run the Python program:

.. code-block:: bash

    python -m run_evadb.py

You should see a list of built-in functions including but not limited to the following:

.. code-block:: bash

            name                                             inputs  ...                                               impl metadata
    0  ArrayCount   [Input_Array NDARRAY ANYTYPE (), Search_Key ANY]  ...  /home/jarulraj3/evadb/evadb/udfs/ndarray/array...       []
    1        Crop  [Frame_Array NDARRAY UINT8 (3, None, None), bb...  ...   /home/jarulraj3/evadb/evadb/udfs/ndarray/crop.py       []
    2     ChatGPT  [query NDARRAY STR (1,), content NDARRAY STR (...  ...        /home/jarulraj3/evadb/evadb/udfs/chatgpt.py       []

    [3 rows x 6 columns]

.. note::
    Go over the :ref:`Python API<python-api>` to learn more about `connect()` and `cursor`.

.. note::

    EvaDB supports additional installation options for extending its functionality. Go over the :doc:`Installation Options <getting-started/installation-options>` for all the available options.

Illustrative AI App
-------------------

Here is a simple, illustrative `MNIST image classification <https://en.wikipedia.org/wiki/MNIST_database>`_ AI app in EvaDB.

.. code-block:: python

    # Connect to EvaDB for running AI queries
    import evadb
    cursor = evadb.connect().cursor()

    # Load the MNIST video into EvaDB
    # Each frame in the loaded MNIST video contains a digit
    cursor.load("mnist.mp4", "MNISTVid", format="video").df()

    # We now construct an AI pipeline to run the image classifier 
    # over all the digit images in the video    

    # Connect to the table with the loaded video
    query = cursor.table("MNISTVid")

    # Run the model on a subset of frames
    # Here, id refers to the frame id
    query = query.filter("id = 30 OR id = 50 OR id = 70 OR id = 0 OR id = 140")

    # We are retrieving the frame "data" and 
    # the output of the Image Classification function on the data 
    query = query.select("data, MnistImageClassifier(data).label")

    # EvaDB uses a lazy query construction technique to improve performance
    # Only calling query.df() will run the query
    response = query.df()

Try out EvaDB by experimenting with the introductory `MNIST notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/evadb/blob/master/tutorials/01-mnist.ipynb>`_.

.. image:: ../../images/reference/mnist.png

.. note::
    Go over the :ref:`Python API<python-api>` to learn more about the functions used in this app.
