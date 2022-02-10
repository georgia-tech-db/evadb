.. _guide-getstarted:

Get Started
=============

Installation
-------
EVA requires Python 3.7 or later. To install EVA, we recommend using pip::

    pip install evadb


Running EVA Server
-------
EVA runs as a client server architecture. So you need to start the server before you can connect to it via various interfaces:::

    eva_server

Querying EVA
-------

- Querying Via Command Line::

EVA offers a CLI interface to query the server for quick testing and debugging::

    eva_client
    >>> UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
    >>> LOAD DATA INFILE 'test_video.mp4' INTO MyVideo;
    >>> SELECT id, data FROM MyVideo WHERE id < 5

- From Python/Jupyter Code::

EVA also provides an API to connect to the server using Python code::

    from src.server.db_api import connect
    import nest_asyncio
    nest_asyncio.apply()
    connection = connect(host = '0.0.0.0', port = 5432) # hostname, port of the server where EVADB is running
    cursor = connection.cursor()

Once the connection is established, you can run queries using the cursor::

    cursor.execute("""SELECT id, Unnest(FastRCNNObjectDetector(data)) FROM MyVideo""")
    response = cursor.fetch_all()

- A sample jupyter notebook the performs object detection using EVA can be found `here <https://github.com/georgia-tech-db/eva/blob/master/tutorials/object_detection.ipynb>`_.