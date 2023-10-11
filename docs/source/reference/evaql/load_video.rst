LOAD VIDEO
==========

.. _load-video:

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