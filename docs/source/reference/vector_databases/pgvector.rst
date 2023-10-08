pgvector
==========

pgvector is an open-source vector similarity search for Postgres. EvaDB uses its native support for Postgres while creating pgvector indices.
The connection to pgvector is based on the `pgvector <https://github.com/pgvector/pgvector>`_ library.

Dependency
----------

* pgvector

Create Index
-----------------

.. code-block:: text

   CREATE INDEX index_name ON table_name (data) USING PGVECTOR;