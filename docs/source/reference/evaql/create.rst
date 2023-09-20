CREATE 
======

.. _sql-create-database:

CREATE DATABASE
---------------

The CREATE DATABASE statement allows us to connect to an external structured data store in EvaDB.

.. code:: text

   CREATE DATABASE [database_connection]
        WITH ENGINE = [database_engine],
        PARAMETERS = [key_value_parameters];

* [database_connection] is the name of the database connection. `[database_connection].[table_name]` will be used as table name to compose SQL queries in EvaDB.
* [database_engine] is the supported database engine. Check :ref:`supported data sources<databases>` for all engine and their available configuration parameters.
* [key_value_parameters] is a list of key-value pairs as arguments to establish a connection.


Examples
~~~~~~~~

.. code:: text

   CREATE DATABASE postgres_data WITH ENGINE = 'postgres', PARAMETERS = {
        "user": "eva", 
        "password": "password",
        "host": "localhost",
        "port": "5432", 
        "database": "evadb"
   };

CREATE TABLE
------------

To create a table, specify the schema of the table.

.. code:: mysql

   CREATE TABLE IF NOT EXISTS MyCSV (
                   id INTEGER UNIQUE,
                   frame_id INTEGER,
                   video_id INTEGER,
                   dataset_name TEXT(30),
                   label TEXT(30),
                   bbox NDARRAY FLOAT32(4),
                   object_id INTEGER
    );

CREATE INDEX
------------

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
* [function_name] is an optional parameter that can be added if the index needs to be construsted on results of a funciton.

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

CREATE FUNCTION
---------------

To register an user-defined function, specify the implementation details of the function.

.. code-block:: sql

    CREATE FUNCTION IF NOT EXISTS FastRCNNObjectDetector
    INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
    OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
            scores NDARRAY FLOAT32(ANYDIM))
    TYPE  Classification
    IMPL  'evadb/functions/fastrcnn_object_detector.py';

CREATE FUNCTION via Type
----------------------------

.. code-block:: sql

   CREATE [OR REPALCE] FUNCTION [IF NOT EXISTS] function_name
   [ FROM ( select ) ]
   TYPE function_type
   [ parameter [ ...] ]

Where the `parameter` is ``key value`` pair.

.. warning::

   For one ``CREATE FUNCTION`` query, we can specify ``OR REPLACE`` or ``IF NOT EXISTS`` or neither, but not both.

.. note::

   Go over :ref:`hf`, :ref:`predict`, and :ref:`forecast` to check examples for creating function via type.

CREATE MATERIALIZED VIEW
------------------------

To create a view with materialized results -- like the outputs of deep learning model, use the following template:

.. code-block:: sql

    CREATE MATERIALIZED VIEW UADETRAC_FastRCNN (id, labels) AS
    SELECT id, FastRCNNObjectDetector(frame).labels 
    FROM UADETRAC
    WHERE id<5;
