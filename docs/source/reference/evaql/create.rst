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

.. _create-udf-train:

CREATE FUNCTION via Training
----------------------------

To register an user-defined function by training a predication model.

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictHouseRent FROM
   (SELECT * FROM HomeRentals)
   TYPE Ludwig
   PREDICT 'rental_price'
   TIME_LIST 120;
   TUNE_FOR_MEMORY False;

CREATE MATERIALIZED VIEW
------------------------

To create a view with materialized results -- like the outputs of deep learning model, use the following template:

.. code-block:: sql

    CREATE MATERIALIZED VIEW UADETRAC_FastRCNN (id, labels) AS
    SELECT id, FastRCNNObjectDetector(frame).labels 
    FROM UADETRAC
    WHERE id<5;
