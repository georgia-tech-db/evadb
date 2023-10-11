CREATE FUNCTION
===============

.. _create-function:

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

