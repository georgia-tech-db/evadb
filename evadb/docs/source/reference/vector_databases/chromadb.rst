ChromaDB
==========

ChromaDB is an open-source embedding database which makes it easy to build LLM apps by making knowledge, facts, and skills pluggable for LLMs.
The connection to ChromaDB is based on the `chromadb <https://pypi.org/project/chromadb/>`_ library.

Dependency
----------

* chromadb

Create Index
-----------------

.. code-block:: text

   CREATE INDEX index_name ON table_name (data) USING CHROMADB;