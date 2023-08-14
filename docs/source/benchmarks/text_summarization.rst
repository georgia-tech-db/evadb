Text summarization benchmark 
====
In this benchmark, we compare the performance of text summarization between EvaDB and MindsDB on `CNN-DailyMail News <https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail>`_.

1. Prepare dataset
----

.. code-block:: bash

   cd benchmark/text_summarization
   bash download_dataset.sh

2. Using EvaDB to summarize the CNN DailyMail News
----

.. note::
 
   Install ray in your EvaDB virtual environment. ``pip install "ray>=1.13.0,<2.5.0"``
   
.. code-block:: bash

   cd benchmark/text_summarization
   python text_summarization_with_evadb.py


3. Using MindsDB to summarize the CNN DailyMail News
----

Prepare sqlite database for MindsDB
****

.. code-block:: bash

   sqlite3 cnn_news_test.db
   > .mode csv
   > .import cnn_news_test.csv cnn_news_test
   > .exit


Install MindsDB
****
Follow the `Setup for Source Code via pip <https://docs.mindsdb.com/setup/self-hosted/pip/source>`_ to install mindsdb.

.. note::

   At the time of this documentation, we need to manully ``pip install evaluate`` for huggingface model to work in MindsDB.

After the installation, we use mysql cli to connect to MindsDB. Replace the port number as needed.

.. code-block:: bash

   mysql -h 127.0.0.1 --port 47335 -u mindsdb -p

Run Experiment
****

Connect the sqlite database we created before.

.. code-block:: sql

   CREATE DATABASE sqlite_datasource
   WITH ENGINE = 'sqlite',
   PARAMETERS = {
     "db_file": "cnn_news_test.db"
   };

Create text summarization model and wait for its readiness.

.. code-block:: sql

   CREATE MODEL mindsdb.hf_bart_sum_20
   PREDICT PRED
   USING
   engine = 'huggingface',
   task = 'summarization',
   model_name = 'sshleifer/distilbart-cnn-12-6',
   input_column = 'article',
   min_output_length = 5,
   max_output_length = 100;

   DESCRIBE mindsdb.hf_bart_sum_20;

Use the model to summarize the CNN DailyMail news

.. code-block:: sql

   CREATE OR REPLACE TABLE sqlite_datasource.cnn_news_summary (
     SELECT PRED
     FROM mindsdb.hf_bart_sum_20
     JOIN sqlite_datasource.cnn_news_test
   );


4. Experiment results
----
Below are nubmers from a server with 56 Intel(R) Xeon(R) CPU E5-2690 v4 @ 2.60GHz and two Quadro P6000 GPU

.. list-table:: Text summarization with ``sshleifer/distilbart-cnn-12-6`` on CNN-DailyMail News

   * -
     - MindsDB
     - EvaDB (off-the-shelf)
     - EvaDB (full GPU utilization)
   * - Time
     - 4 hours 45 mins 47.56 secs
     - 1 hour 9 mins 39.8 secs
     - 42 mins 50.22 secs


