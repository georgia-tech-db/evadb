Docker
====

You can launch the EVA server using Docker either locally or on a server with GPUs:

.. code-block:: bash

    docker run --name eva_server --gpus all -p 8803:8803 evadbai/evaserver
