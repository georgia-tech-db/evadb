CREATE 
======

CREATE TABLE
----

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

CREATE UDF
----

To register an user-defined function, specify the implementation details of the UDF.

.. code-block:: sql

    CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
    INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
    OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
            scores NDARRAY FLOAT32(ANYDIM))
    TYPE  Classification
    IMPL  'eva/udfs/fastrcnn_object_detector.py';

CREATE MATERIALIZED VIEW
----

To create a view with materialized results -- like the outputs of deep learning model, use the following template:

.. code-block:: sql

    CREATE MATERIALIZED VIEW UADETRAC_FastRCNN (id, labels) AS
    SELECT id, FastRCNNObjectDetector(frame).labels 
    FROM UADETRAC
    WHERE id<5;