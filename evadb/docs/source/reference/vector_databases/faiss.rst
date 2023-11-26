Faiss
==========

Faiss is a library for efficient similarity search and clustering of dense vectors.
It contains algorithms that search in sets of vectors of any size, up to ones that possibly do not fit in RAM.
The connection to Faiss is based on the `faiss-cpu <https://faiss.ai/index.html>`_ or `faiss-gpu <https://faiss.ai/index.html>`_ library.

Dependency
----------

* faiss-cpu (or) faiss-gpu

Create Index
-----------------

.. code-block:: text

   CREATE INDEX index_name ON table_name (data) USING FAISS;