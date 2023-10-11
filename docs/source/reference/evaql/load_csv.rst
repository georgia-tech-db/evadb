LOAD CSV
==========

.. _load-csv:

To **LOAD** a CSV file, we need to first specify the table schema.

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

   LOAD CSV 'test_metadata.csv' INTO MyCSV;

-  **test_metadata.csv** needs to be loaded onto the server using
   **LOAD** statement.
-  The CSV file may contain additional columns. EvaDB will only load
   the columns listed in the defined schema.
