Qdrant
==========

Qdrant is a vector similarity search engine. Qdrant’s expanding features allow for all sorts of neural network or semantic-based matching, faceted search, and other applications.
The connection to Qdrant is based on the `qdrant-client <https://qdrant.tech/documentation/>`_ library.

Dependency
----------

* qdrant-client

Create Index
-----------------

.. code-block:: text

   CREATE INDEX index_name ON table_name (data) USING QDRANT;