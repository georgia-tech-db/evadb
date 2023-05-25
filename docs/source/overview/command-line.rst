.. _guide-getstarted:

Command Line Client
====

Besides the Jupyter notebook interface, EVA also exports a command line interface for querying the server. This interface allows for quick querying from the terminal:

.. code-block:: bash

    >>> eva_client
    eva=# LOAD VIDEO "mnist.mp4" INTO MNISTVid;
    @status: ResponseStatus.SUCCESS
    @batch:

    0 Video successfully added at location: mnist.p4
    @query_time: 0.045

    eva=# SELECT id, data FROM MNISTVid WHERE id < 1000;
    @status: ResponseStatus.SUCCESS
    @batch:
                mnistvid.id     mnistvid.data 
        0          0             [[[ 0 2 0]\n [0 0 0]\n...         
        1          1             [[[ 2 2 0]\n [1 1 0]\n...         
        2          2             [[[ 2 2 0]\n [1 2 2]\n...         
        ..       ...
        997        997           [[[ 0 2 0]\n [0 0 0]\n...         
        998        998           [[[ 0 2 0]\n [0 0 0]\n...         
        999        999           [[[ 2 2 0]\n [1 1 0]\n...         

    [1000 rows x 2 columns]
    @query_time: 0.216  

    eva=# exit
