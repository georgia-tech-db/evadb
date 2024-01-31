Marqo
==========

Marqo is more than a vector database, it's an end-to-end vector search engine for both text and images. 
Vector generation, storage and retrieval are handled out of the box through a single API. 
Connection is based on the `marqo <https://github.com/marqo-ai/py-marqo>`_ client library.

Dependency
----------

* marqo==2.1.0


Setup 
-----

To use marqo, you need a URL and API key to your instance. 
Here are `instructions to setup local instance <https://github.com/marqo-ai/marqo#getting-started>`_. 
Cloud offering can also be used.


Create Index
-----------------

.. code-block:: sql

   CREATE INDEX index_name ON table_name (data) USING MARQO;