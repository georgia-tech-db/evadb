.. _guide-getstarted:

Getting Started
====

Installation
----

EVA supports Python (versions 3.7 and higher). To install EVA, we recommend using the pip package manager::

    pip install evadb


Starting EVA Server
----

EVA is based on a `client-server architecture <https://www.postgresql.org/docs/15/tutorial-arch.html>`_. To start the server, run the following command on the terminal:

    eva_server &

Running Queries on EVA
----

EVA exports two interfaces for users: (1) 
`Jupyter Notebook <https://jupyter.org/try-jupyter/retro/notebooks/?path=notebooks/Intro.ipynb>`_ interface and (2) command line interface.

Jupyter Notebook Interface:
~~~~

To connect to the EVA server in the notebook, use the following Python code::

    from src.server.db_api import connect
    import nest_asyncio
    nest_asyncio.apply()

    # hostname and port of the server where EVA is running
    connection = connect(host = '0.0.0.0', port = 5432) 
    cursor = connection.cursor()

After the connection is established, we can use the connection's cursor to run queries::

    # load a video into the EVA server
    cursor.execute("""LOAD FILE "mnist.mp4" INTO MNISTVid;""")
    response = cursor.fetch_all()
    print(response)

    # run a query over the video 
    # retrieve the output of the MNIST CNN model that is included
    # in EVA as a built-in user-defined function
    cursor.execute("""SELECT id, MnistCNN(data).label 
                      FROM MNISTVid 
                      WHERE id < 5;""")
    response = cursor.fetch_all()
    print(response)

.. admonition:: Illustrative Jupyter Notebook

   Here is an `illustrative Jupyter notebook <https://evadb.readthedocs.io/en/latest/source/tutorials/01-mnist.html>`_ focusing on MNIST image classification using EVA.

Command Line Interface:
~~~~

EVA also exports a command line interface (CLI) to query the server for quick testing::

    >>> eva_client
    eva=# LOAD FILE "eva/data/mnist/mnist.mp4" INTO MNISTVid;
    @status: ResponseStatus.SUCCESS
    @batch:

    0 Video successfully added at location: data/mnist/mnist.p4
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