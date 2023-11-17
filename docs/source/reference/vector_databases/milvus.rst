Milvus
==========

Milvus is an open-source, distributed vector database designed for similarity search and analytics on large-scale vector data.
The connection to Milvus is based on the `pymilvus <https://pymilvus.readthedocs.io/en/latest>`_ library.

Dependency
----------

* pymilvus

Parameters
----------

To use Milvus you must have a URI to a running Milvus instance. Here are the `instructions to spin up a local instance <https://milvus.io/docs/install_standalone-docker.md>`_.
If you are running it locally, the Milvus instance should be running on ``http://localhost:19530``. Please be sure that the Milvus version is >= 2.3.0. Below are values that the Milvus integration uses:

* `MILVUS_URI` is the URI of the Milvus instance (which would be ``http://localhost:19530`` when running locally). **This value is required**
* `MILVUS_USER` is the name of the user for the Milvus instance.
* `MILVUS_PASSWORD` is the password of the user for the Milvus instance.
* `MILVUS_DB_NAME` is the name of the database to be used. This will default to the `default` database if not provided.
* `MILVUS_TOKEN` is the authorization token for the Milvus instance. 

The above values can either be set via the ``SET`` statement, or in the os environment fields "MILVUS_URI", "MILVUS_USER", "MILVUS_PASSWORD", "MILVUS_DB_NAME", and "MILVUS_TOKEN"


.. code-block:: sql

   SET MILVUS_URI = 'http://localhost:19530';


Create Index
-----------------

.. code-block:: sql

   CREATE INDEX index_name ON table_name (data) USING MILVUS;
