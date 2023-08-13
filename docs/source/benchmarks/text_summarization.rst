Text summarization benchmark 
====
In this benchmark, we compare the performance of text summarization between EvaDB and MindsDB on `CNN-DailyMail News <https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail>`.

1. Prepare dataset
----

.. code-block: bash

   cd benchmark/text_summarization
   bash download_dataset.sh

2. Using EvaDB to summarize the CNN DailyMail News
----

.. note::
 
   Install ray in your EvaDB virtual environment. ``pip install "ray>=1.13.0,<2.5.0"``
   
.. code-block: bash

   cd benchmark/text_summarization
   python text_summarization_with_evadb.py


3. Using mindsdb to summarize the CNN DailyMail News
----

TODO


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


