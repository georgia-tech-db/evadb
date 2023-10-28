CREATE INDEX
============

.. _create-index:

The CREATE INDEX statement allows us to construct an EvaDB based index to accelerate semantic based searching.
The index can be created on either a column of a table directly or outputs from a function running on a column of a table.

.. code:: sql
   
   CREATE INDEX [index_name]
      ON [table_name] ([column_name])
      USING [index_method]

   CREATE INDEX [index_name]
      ON [table_name] ([function_name]([column_name]))
      USING [index_method]

* [index_name] is the name the of constructed index.
* [table_name] is the name of the table, on which the index is created.
* [column_name] is the name of one of the column in the table. We currently only support creating index on single column of a table.
* [function_name] is an optional parameter that can be added if the index needs to be constructed on results of a function.

Examples
~~~~~~~~

.. code:: sql

   CREATE INDEX reddit_index
   ON reddit_dataset (data)
   USING FAISS

   CREATE INDEX func_reddit_index
   ON reddit_dataset (SiftFeatureExtractor(data))
   USING QDRANT

You can check out :ref:`similarity search use case<image-search>` about how to use index automatically.
