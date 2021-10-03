.. _guide-getstarted:

Get Started
=============

Installation
-------
If you haven't installed EVA yet, you can do so by following instructions `given here <https://github.com/georgia-tech-db/eva#installation>`_

Running EVA Server
-------
EVA runs as a client-server architecture. So you need to start the server before you can connect to it via various interfaces::

    python eva.py

Querying EVA
-------

- Querying Via Command Line::

You can use the CLI of EVA to do some quick testing or verifying if the installation was succesful::

    python eva_cmd_client.py
    >>> UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
    >>> LOAD DATA INFILE 'test_video.mp4' INTO MyVideo;
    >>> SELECT id, data FROM MyVideo WHERE id < 5

- Experimenting With Jupyter Notebook::

You can connect to the EVA server via a Jupyter Notebook as well, just copy paste the following snipped::

    from src.server.db_api import connect
    import nest_asyncio
    nest_asyncio.apply()
    connection = connect(host = '0.0.0.0', port = 5432) # hostname, port of the server where EVADB is running
    cursor = connection.cursor()

Once the connection is established, you can run queries using the cursor::

    cursor.execute("""SELECT id, Unnest(FastRCNNObjectDetector(data)) FROM MyVideo""")
    response = cursor.fetch_all()
