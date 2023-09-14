.. _text-summarization:

Text Summarization 
==================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/12-query-pdf.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/12-query-pdf.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/12-query-pdf.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>


Introduction
------------

In this tutorial, we present how to use ``HuggingFace`` models in EvaDB to summarize and classify text. In particular, we will first load ``PDF`` documents into ``EvaDB`` using the ``LOAD PDF`` statement. The text in each paragraph from the PDF is automatically stored in the ``data`` column of a table for subsequent analysis. We then run text summarization and text classification AI queries on the ``data`` column obtained from the loaded ``PDF`` documents.

EvaDB makes it easy to process text using its built-in support for ``HuggingFace``.

.. include:: ../shared/evadb.rst

We will assume that the input ``pdf_sample1`` PDF is loaded into ``EvaDB``. To download the PDF and load it into ``EvaDB``, see the complete `text summarization notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/12-query-pdf.ipynb>`_.


Create Text Summarization and Classification Functions
------------------------------------------------------

To create custom ``TextSummarizer`` and ``TextClassifier`` functions, use the ``CREATE FUNCTION`` statement. In these queries, we leverage EvaDB's built-in support for ``HuggingFace`` models. We only need to specify the ``task`` and the ``model`` parameters in the query to create these functions:

.. code-block:: sql

        CREATE FUNCTION IF NOT EXISTS TextSummarizer
        TYPE HuggingFace
        TASK 'summarization'
        MODEL 'facebook/bart-large-cnn';

        CREATE FUNCTION IF NOT EXISTS TextClassifier
        TYPE HuggingFace
        TASK 'text-classification'
        MODEL 'distilbert-base-uncased-finetuned-sst-2-english';

.. note::
    
    EvaDB has built-in support for a wide range of :ref:`HuggingFace<hf>` models.

AI Query Using Registered Functions
-----------------------------------

After registering these two functions, we use them in a single AI query over the ``data`` column to retrieve a subset of paragraphs from the loaded ``PDF`` documents with `negative` sentiment:

.. code-block:: sql

        CREATE TABLE text_summary AS 
        SELECT data, TextSummarizer(data) 
        FROM MyPDFs
        WHERE page = 1 
              AND paragraph >= 1 AND paragraph <= 3
              AND TextClassifier(data).label = 'NEGATIVE';

Here, the ``TextClassifier`` function is applied on the ``data`` column of the ``pdf_sample1`` PDF loaded into EvaDB and its output is used to filter out a subset of paragraphs with `negative sentiment`. 

EvaDB's query optimizer automatically applies the earlier predicates on page number and paragraph numbers to (e.g., ``page = 1``) to avoid running the expensive ``TextClassifier`` function on all the rows in the table. After filtering out a subset of paragraphs, EvaDB applies the ``TextSummarizer`` function to derive their summaries.

Here is the query's output ``DataFrame``:

.. code-block:: 

    +--------------------------------------------------------------+--------------------------------------------------------------+
    |                         mypdfs.data                          |                 textsummarizer.summary_text                  |
    +--------------------------------------------------------------+--------------------------------------------------------------+
    | DEFINATION  Specialized connective tissue with          ... | Specialized connective tissue with fluid matrix. Erythro ... |
    | PHYSICAL CHARACTERISTICS ( 1 )  COLOUR   -- Red  ( 2 )  ... | The temperature is 38° C / 100.4° F. The body weight is  ... |
    +--------------------------------------------------------------+--------------------------------------------------------------+


.. include:: ../shared/nlp.rst

.. include:: ../shared/footer.rst
