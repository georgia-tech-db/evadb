.. _getting-started:

Getting Started
=================

Install EvaDB 
-------------

To install EvaDB, we recommend using the `pip` package manager. EvaDB only supports Python versions greater than or equal to `3.9`.

1. Create a new `virtual environment <https://docs.python-guide.org
/dev/virtualenvs/>`_ called `evadb-venv`.

.. code-block:: bash

    python -m venv evadb-venv

.. warning::

    EvaDB only supports Python versions greater than or equal to `3.9`. You can check the version of your Python interpreter by running `python --version` on the terminal.

Now, activate the virtual environment:

.. code-block:: bash

    source evadb-venv/bin/activate

2. Once inside the virtual environment, run the command below to mitigate the dependency issues.

.. code-block:: bash

   pip install --upgrade pip setuptools wheel

3. Install EvaDB

.. code-block:: bash

   pip install --upgrade evadb

.. note::

    The `--upgrade` option ensure that the latest version of EvaDB is installed.

4. Verify EvaDB installation

.. code-block:: bash

   pip freeze

You should see a list of installed packages including but not limited to the following:

.. code-block:: bash

   Package           Version
   ----------------- -------
   aenum             3.1.15
   decorator         5.1.1
   diskcache         5.6.3
   evadb             0.3.7
   greenlet          2.0.2
   lark              1.1.7
   numpy             1.25.2
   pandas            2.1.0
   ...

5. Run EvaDB

Copy the following Python code to a file called `run_evadb.py`.

The program runs a SQL query for listing all the built-in functions in EvaDB. It consists of importing and connecting to EvaDB, and then running the query. The query's result is returned as a Dataframe.

.. code-block:: python

   # Import the EvaDB package 
   import evadb

   # Connect to EvaDB and get a database cursor for running queries
   cursor = evadb.connect().cursor()

   # List all the built-in functions in EvaDB
   print(cursor.query("SHOW FUNCTIONS;").df())

Now, run the Python program:

.. code-block:: bash

    python -m run_evadb.py

You should see a list of built-in functions (with different filenames) including but not limited to the following:

.. code-block:: bash

            name                                             inputs  ...                                               impl metadata
    0  ArrayCount   [Input_Array NDARRAY ANYTYPE (), Search_Key ANY]  ...  /home/username/evadb/evadb-venv/functions/ndarray/array...       []
    1        Crop  [Frame_Array NDARRAY UINT8 (3, None, None), bb...  ...   /home/username/evadb/evadb-venv/functions/ndarray/crop.py       []
    2     ChatGPT  [query NDARRAY STR (1,), content NDARRAY STR (...  ...        /home/username/evadb/evadb/evadb-venv/chatgpt.py       []

    [3 rows x 6 columns]

.. note::
    Go over the :ref:`Python API<python-api>` page to learn more about `connect()` and `cursor`.

.. note::

    EvaDB supports additional installation options for extending its functionality. Go over the :doc:`Installation Options <getting-started/installation-options>` page for all the available options.

Illustrative AI Query
---------------------

Here is an illustrative EvaQL query that analyzes the sentiment of restaurant food reviews and responds to them.

.. code-block:: sql
    
    --- This AI query analyses the sentiment of restaurant food reviews stored 
    --- in a database table and generates a response to negative food reviews
    --- using another ChatGPT call to address the concerns shared in the review
    SELECT
        ChatGPT("Respond to the review with a solution to address the reviewer's concern",
        review)     
    FROM
        postgres_data.review_table     
    WHERE
        ChatGPT("Is the review positive or negative?", review) = "negative";

More details on this usecase is available in the :ref:`Sentiment Analysis <sentiment-analysis>` page. 

Try out EvaDB by experimenting with the complete `sentiment analysis notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/14-food-review-tone-analysis-and-response.ipynb>`_ 🙂

.. include:: ../shared/designs/design2.rst