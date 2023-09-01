.. _Getting Started:

Getting Started
=================

Install EvaDB Locally using pip
----------------------

To install EvaDB, we recommend using the `pip` package manager:

1. Create a new virtual environment called `evadb-venv`.

.. code-block:: bash

    python -m venv evadb-venv

Now, activate it:

.. code-block:: bash

    source evadb-venv/bin/activate

2. Once inside the virtual environment, run the command below to mitigate the dependency issues:

.. code-block:: bash

   pip install --upgrade pip setuptools wheel

3. Install EvaDB:

.. code-block:: bash

   pip install evadb

4. Verify EvaDB installation:

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

5. Run a query using EvaDB

Run the following `Python` program to obtain a connection to EvaDB and run the `SHOW UDFS;` query. This query lists all the built-in functions.

.. code-block:: python

   import evadb
   cursor = evadb.connect().cursor()
   print(cursor.query("SHOW UDFS;").df())

.. note::

   Go over the :ref:`Python API<python-api>` for `connect` and `cursor`-related documentation.

.. note::

    EvaDB supports additional installation options for extending its functionality. Refer to the see :doc:`Installation Guide <getting-started/install-guide>` for all the available options.

Write Your AI App
--------------------------

Here is an illustrative MNIST digit classification app using EvaDB.

.. code-block:: python

    # Connect to EvaDB for running AI queries
    import evadb
    cursor = evadb.connect().cursor()

    # Load the MNIST video into EvaDB
    cursor.load("mnist.mp4", "MNISTVid", format="video").df()

    # We now construct an AI pipeline to run the image classifier 
    # over all the digit images in the video    
    # Each frame in the loaded MNIST video contains a digit

    # Connect to the table with the loaded video
    query = cursor.table("MNISTVid")

    # Run the model on a subset of frames
    # Here, id refers to the frame id
    query = query.filter("id = 30 OR id = 50 OR id = 70")

    # We are retrieving the frame "data" and 
    # the output of the Image Classification function on the data 
    query = query.select("data, MnistImageClassifier(data).label")

    # EvaDB uses a lazy query construction technique to improve performance
    # Only calling query.df() will run the query
    response = query.df()



Check out our `Google Colab <https://colab.research.google.com/github/georgia-tech-db/evadb/blob/master/tutorials/01-mnist.ipynb>`_ for working example.

.. image:: ../../images/reference/mnist.png
