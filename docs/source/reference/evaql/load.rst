.. _sql-load:

LOAD
====

.. _1-load-video-from-filesystem:

LOAD VIDEO FROM FILESYSTEM
--------------------------

.. code:: mysql

   LOAD VIDEO 'test_video.mp4' INTO MyVideo;


-  **test_video.mp4** is the location of the video file in the filesystem on the client.
-  **MyVideo** is the name of the table in EvaDB where this video is loaded. Subsequent queries over the video must refer to this table name.

When a video is loaded, there is no need to specify the schema for the video table. EvaDB automatically generates the following schema with two columns:
``id`` and ``data``, that correspond to the frame id and frame content (in Numpy format).

.. _2-load-video-from-s3:

LOAD VIDEO FROM S3
------------------

.. code:: mysql

   LOAD VIDEO 's3://bucket/dummy.avi' INTO MyVideo;
   LOAD VIDEO 's3://bucket/eva_videos/*.mp4' INTO MyVideos;

The videos are downloaded to a directory that can be configured in the EvaDB configuration file under `storage:s3_download_dir`. The default directory is ``evadb_data/s3_downloads``.

.. _3-load-image-from-file:

LOAD IMAGE FROM FILESYSTEM
--------------------------

.. code:: mysql

   LOAD IMAGE 'test_image.jpg' INTO MyImage;

Images are loaded similarity to videos, each tuple in an image table represents an image. EvaDB automatically generates 
the following schema with two columns: ``name`` and ``data``, that correspond to the image name and the image data.

.. _4-load-the-csv-file:

LOAD CSV 
--------

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
