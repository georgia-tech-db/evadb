LOAD
====

.. _1-load-the-video-file:

LOAD VIDEO 
----

.. code:: mysql

   LOAD FILE 'test_video.mp4' INTO MyVideo;

   --- Alternate syntax that explicitly specifies format
   LOAD FILE 'dummy.avi' INTO MyVideo WITH FORMAT VIDEO;

-  **test_video.mp4** is the location of the video file in the filesystem on the client.
-  **MyVideo** is the name of the table in EVA where this video is loaded. Subsequent queries over the video must refer to this table name.

When a video is loaded, there is no need to specify the schema for the video table. EVA automatically generates the following schema with two columns:
``id`` and ``data``, that correspond to the frame id and frame content (in Numpy format).

.. _2-load-the-csv-file:

LOAD CSV 
----

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

   LOAD FILE 'test_metadata.csv' INTO MyCSV WITH FORMAT CSV;

-  **test_metadata.csv** needs to be loaded onto the server using
   **LOAD** statement.
-  The CSV file may contain additional columns. EVA will only load
   the columns listed in the defined schema.
-  **WITH FORMAT CSV** is required to distinguish between videos and CSV files.
