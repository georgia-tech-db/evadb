.. _Getting Started:

Getting Started
=================

Install EvaDB 
-------------

To install EvaDB, we recommend using the `pip` package manager.

1. Create a new `virtual environment<<https://docs.python-guide.org
/dev/virtualenvs/>`_ called `evadb-venv`.

.. code-block:: bash

    python -m venv evadb-venv

Now, activate the virtual environment.

.. code-block:: bash

    source evadb-venv/bin/activate

2. Once inside the virtual environment, run the command below to mitigate the dependency issues.

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

To run a `SHOW UDFS;` query, use the following Python program. It consists of importing and connecting to EvaDB, and then running a query. The query result is returned as a Dataframe. The `SHOW UDFS;` query  lists all the built-in functions in EvaDB. 

.. code-block:: python

   import evadb
   cursor = evadb.connect().cursor()
   print(cursor.query("SHOW UDFS;").df())

.. note::
    Go over the :ref:`Python API<python-api>` to learn more about `connect()` and `cursor`.

.. note::

    EvaDB supports additional installation options for extending its functionality. Go over the :doc:`Installation Guide <getting-started/install-guide>` for all the available options.

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