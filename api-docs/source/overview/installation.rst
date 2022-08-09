.. _guide-getstarted:

Getting Started
=============

Installation
--------------
EVA requires Python 3.7 or later. To install EVA, we recommend using pip::

    pip install evadb


Starting EVA Server
---------------------
EVA uses a client server architecture. To start the server, run the followign command:::

    eva_server &

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

    cursor.execute("""SELECT id, Unnest(FastRCNNObjectDetector(data)) FROM MyVideo""")
    response = cursor.fetch_all()

.. admonition:: Sample Jupyter Notebook.

   An illustrative notebook focusing on object detection using EVA is located `here <https://github.com/georgia-tech-db/eva/blob/master/tutorials/object_detection.ipynb>`_.

- Command Line Interface::

EVA offers a command line interface (CLI) to query the server for quick testing and debugging::

    eva_client
    >>> UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
    >>> LOAD DATA INFILE 'test_video.mp4' INTO MyVideo;
    >>> SELECT id, data FROM MyVideo WHERE id < 5
