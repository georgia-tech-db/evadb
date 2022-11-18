.. _guide-getstarted:

Getting Started
=============

Installation
--------------
EVA supports Python (versions 3.7 and higher). To install EVA, we recommend using pip::

    pip install evadb


Starting EVA Server
---------------------
EVA uses a client server architecture. To start the server, run the followign command:::

    python eva/eva_server &

Querying EVA
--------------

EVA exports two interfaces for clients.

- Jupyter Notebook Interface::

EVA provides an API for connecting to the server in Python code::

    from src.server.db_api import connect
    import nest_asyncio
    nest_asyncio.apply()
    connection = connect(host = '0.0.0.0', port = 5432) # hostname, port of the server where EVADB is running
    cursor = connection.cursor()

Once the connection is established, you can run queries using the cursor::

    cursor.execute("""LOAD FILE "mnist.mp4" INTO MNISTVid;""")
    response = cursor.fetch_all()
    print(response)
    cursor.execute("""SELECT data, MnistCNN(data).label 
                      FROM MNISTVid 
                      WHERE id < 5;""")
    response = cursor.fetch_all()
    print(response)

.. admonition:: Illustrative Jupyter Notebook.

   An illustrative notebook focusing on object detection using EVA is located `here <https://github.com/georgia-tech-db/eva/blob/master/tutorials/01-mnist.ipynb>`_.

- Command Line Interface::

EVA also exports a command line interface (CLI) to query the server for quick testing and debugging::

    python eva/eva_client
    >>> LOAD FILE "eva/data/mnist/mnist.mp4" INTO MNISTVid;
    >>> SELECT id, data FROM MNISTVid WHERE id < 5;
