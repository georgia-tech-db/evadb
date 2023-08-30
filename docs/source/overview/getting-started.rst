
Getting Started
=================

Install EvaDB
-----------------------

EvaDB supports Python (versions >= `3.8`). To install EvaDB, we recommend using the `pip` package manager:

.. code-block:: bash

    pip install evadb

.. note::

    EvaDB provides multiple installation options for extending its functionalities. 
    Please see :doc:`Installation Guide <getting-started/install-guide>` for all options.

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
