Pinecone
==========

Pinecone is a managed, cloud-native vector database with a simple API and no infrastructure hassles.
The connection to Pinecone is based on the `pinecone-client <https://docs.pinecone.io/docs/python-client>`_ library.

Dependency
----------

* pinecone-client

Parameters
----------

To use pinecone you must have an API key. Here are the `installation instructions <https://docs.pinecone.io/docs/quickstart>`_.
Once you get an API key, you can also view the corresponding environment details in the same page. Both of the above details
will be needed to establish a connection to the server.

* `API_KEY` is the Pinecone API key.
* `ENVIRONMENT` is the environment detail for the API key.

The above values can either be set in the evadb.yml config file, or in the os environment fields "PINECONE_API_KEY", "PINECONE_ENV"

Create Index
-----------------

.. code-block:: text

   CREATE INDEX index_name ON table_name (data) USING PINECONE;