:orphan:

Docker
======

You can launch the EvaDB server using Docker either locally or on a server with GPUs:

.. code-block:: bash

    docker run --name evadb_server --gpus all -p 8803:8803 evadbai/evaserver
