CREATE TABLE
============

.. _create-table:

To create a table, we can specify the schema of the table.

.. code-block::

   CREATE TABLE [IF NOT EXISTS] table_name ( [
     column_name data_type
     [, ... ]
   ] );

Below is an example:

.. code:: mysql

   CREATE TABLE IF NOT EXISTS MyCSV (
     id INTEGER UNIQUE,
     frame_id INTEGER,
     video_id INTEGER,
     dataset_name TEXT,
     label TEXT,
     bbox NDARRAY FLOAT32(4),
     object_id INTEGER
   );

Below are all supported column types:

* INTEGER
* TEXT
* FLOAT
* NDARRAY 
* BOOLEAN

.. note::

   Check `NdArrayType <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/catalog/catalog_type.py>`_ for available NDARRAY types.

We can also create table from the output of a ``SELECT`` query.

.. code-block::

   CREATE TABLE [IF NOT EXISTS] table_name 
   AS select_query

Below is an example:

.. code-block:: sql

    CREATE TABLE UADETRAC_FastRCNN AS
    SELECT id, FastRCNNObjectDetector(frame).labels 
    FROM UADETRAC
    WHERE id<5;


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

   CREATE [OR REPLACE] FUNCTION [IF NOT EXISTS] function_name
   [ FROM ( select ) ]
   TYPE function_type
   [ parameter [ ...] ]

Where the `parameter` is ``key value`` pair.

.. warning::

   For one ``CREATE FUNCTION`` query, we can specify ``OR REPLACE`` or ``IF NOT EXISTS`` or neither, but not both.

.. note::

   Go over :ref:`hf`, :ref:`ludwig`, and :ref:`forecast` to check examples for creating function via type.

