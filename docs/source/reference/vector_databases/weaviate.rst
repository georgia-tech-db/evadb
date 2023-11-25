Weaviate
==========

Weaviate is an open-source vector database designed for scalability and rich querying capabilities. It allows for semantic search, automated vectorization, and supports large language model (LLM) integration.
The connection to Weaviate is based on the `weaviate-client <https://weaviate.io/developers/weaviate/client-libraries/python>`_ library.

Dependency
----------

* weaviate-client

Parameters
----------

To use Weaviate, you need an API key and a URL of your Weaviate instance. Here are the `instructions for setting up a Weaviate instance <https://weaviate.io/developers/weaviate/quickstart>`_. After setting up your instance, you will find the API key and URL on the Details tab in Weaviate Cloud Services (WCS) dashboard. These details are essential for establishing a connection to the Weaviate server.

* `WEAVIATE_API_KEY` is the API key for your Weaviate instance.
* `WEAVIATE_API_URL` is the URL of your Weaviate instance.

The above values can either be set via the ``SET`` statement, or in the os environment fields "WEAVIATE_API_KEY", "WEAVIATE_API_URL"

Create Collection
-----------------

Weaviate uses collections (similar to 'classes') to store data. To create a collection in Weaviate, use the following SQL command in EvaDB:

.. code-block:: sql

   CREATE INDEX collection_name ON table_name (data) USING WEAVIATE;

This command creates a collection in Weaviate with the specified name, linked to the table in EvaDB. You can also specify vectorizer settings and other configurations for the collection as needed.