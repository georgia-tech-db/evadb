ChatGPT + Postgres Tutorial
===========================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/14-food-review-tone-analysis-and-response.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/14-food-review-tone-analysis-and-response.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/14-food-review-tone-analysis-and-response.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>

In this tutorial, we demonstrate how to use EvaDB + ChatGPT to analyze the tone of food reviews stored in PostgreSQL. Then, based on the analysis, we further use
EvaDB + ChatGPT to address negative reviews by proposing a solution to the customer. 

For this use case, we assume user has a Postgres server running locally. You can also check our notebook above to skip Postgres setup.

1. Connect to EvaDB
---------------------

.. code-block:: python

    import evadb
    cursor = evadb.connect().cursor()

2. Connect to an Existing Postgres Database
---------------------------------------------

.. tab-set::
    
    .. tab-item:: Python

        .. code-block:: python

            params = {
                "user": "eva",
                "password": "password",
                "host": "localhost",
                "port": "5432",
                "database": "evadb",
            }
            query = f"CREATE DATABASE postgres_data WITH ENGINE = 'postgres', PARAMETERS = {params};"
            cursor.query(query).df()

    .. tab-item:: SQL 

        .. code-block:: text

            CREATE DATABASE postgres_data WITH ENGINE = 'postgres', PARAMETERS = {
                "user": "eva",
                "password": "password",
                "host": "localhost",
                "port": "5432",
                "database": "evadb"
            }

3. Sentiment Analysis of Food Review using ChatGPT
---------------------------------------------------

We then use EvaDB + ChatGPT to analyze whether the review is "positive" or "negative" with customized ChatGPT prompt. For this use case,
we assume reviews have been already loaded into the table inside PostgreSQL. 
You can check our `Jupyter Notebook <https://github.com/georgia-tech-db/eva/blob/staging/tutorials/14-food-review-tone-analysis-and-response.ipynb>`__ for how to load data.

.. tab-set::
    
    .. tab-item:: Python

        .. code-block:: python

            cursor.query("""
                SELECT ChatGPT(
                    "Is the review positive or negative. Only reply 'positive' or 'negative'. Here are examples. The food is very bad: negative. The food is very good: positive.",
                    review)
                FROM postgres_data.review_table;
            """).df()

    .. tab-item:: SQL 

        .. code-block:: sql

            SELECT ChatGPT(
                "Is the review positive or negative. Only reply 'positive' or 'negative'. Here are examples. The food is very bad: negative. The food is very good: positive.",
                review)
            FROM postgres_data.review_table;

This will return tone analysis results for existing reviews.

.. code-block:: 

    +------------------------------+
    |             chatgpt.response |
    |------------------------------|
    |                     negative |
    |                     positive |
    |                     negative |
    +------------------------------+

4. Response to Negative Reviews using ChatGPT
---------------------------------------------

.. tab-set::
    
    .. tab-item:: Python

        .. code-block:: python

            cursor.query("""
                SELECT ChatGPT(
                    "Respond the the review with solution to address the review's concern",
                    review)
                FROM postgres_data.review_table
                WHERE ChatGPT(
                    "Is the review positive or negative. Only reply 'positive' or 'negative'. Here are examples. The food is very bad: negative. The food is very good: positive.",
                    review) = "negative";
            """).df()

    .. tab-item:: SQL 

        .. code-block:: sql

            SELECT ChatGPT(
                    "Respond the the review with solution to address the review's concern",
                    review)
            FROM postgres_data.review_table
            WHERE ChatGPT(
                "Is the review positive or negative. Only reply 'positive' or 'negative'. Here are examples. The food is very bad: negative. The food is very good: positive.",
                review) = "negative";

This query will first filter out positive reviews and then apply ChatGPT again to create response to negative reviews. This will give results.

.. code-block:: 

    +----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    |                                                                                                                                                                                                                                                                             chatgpt.response |
    |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | Dear valued customer, Thank you for bringing this matter to our attention. We apologize for the inconvenience caused by the excessive saltiness of your fried rice. We understand how important it is to have a satisfying dining experience, and we would like to make it right for you ... |
    | Dear [Customer's Name], Thank you for bringing this issue to our attention. We apologize for the inconvenience caused by the missing chicken sandwich in your takeout order. We understand how frustrating it can be when an item is missing from your meal. To address this concern, we ... |
    +----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Check out our `Jupyter Notebook <https://github.com/georgia-tech-db/evadb/blob/staging/tutorials/14-food-review-tone-analysis-and-response.ipynb>`__ for working example.
