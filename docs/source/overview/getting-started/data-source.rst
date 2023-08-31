Integrate Data Source
=====================

EvaDB supports an extensive data sources for both structured and unstructured data.

1. Connect to an existing structured data source.

.. code-block:: python

   cursor.query("""
        CREATE DATABASE postgres_data WITH ENGINE = 'postgres', PARAMETERS = {
                "user": "eva",
 		"password": "password",
 		"host": "localhost",
 		"port": "5432",
 		"database": "evadb"
     	};""").df()
        
The above query connects to an exsiting Postgres database, which allows us to build AI applications in EvaDB without data migration.
For example, the following query previews the available data using :ref:`SELECT<sql-select>`.

.. code-block:: python

   cursor.query("SELECT * FROM postgres_data.food_review;").df()

We can also run native queries in the connected database by the :ref:`USE<sql-use>` statement.

.. code-block:: python

   cursor.query("""
        USE postgres_data {
                INSERT INTO food_review (name, review) VALUES ('Customer 1', 'I ordered fried rice but it is too salty.')
        };""").df()


2. Load unstructured data. EvaDB supports a wide range of type of unstructured data. Below are some example:

.. code-block:: python
   
   cursor.query(
       "LOAD IMAGE 'reddit-images/*.jpg' INTO reddit_dataset;"
   ).df()

We load the local reddit image dataset into EvaDB. 

.. code-block:: python

   cursor.query("LOAD VIDEO 's3://bucket/eva_videos/mnist.mp4' INTO MNISTVid;").df()

We load the MNIST video from s3 bucket into EvaDB.

.. note::

   Check :ref:`LOAD statement<sql-load>` for all types of supported unstructured data.
   
