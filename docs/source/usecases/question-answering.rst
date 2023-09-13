.. _question-answering:

Question Answering 
==================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/08-chatgpt.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/08-chatgpt.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/08-chatgpt.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>


Introduction
------------

In this tutorial, we present how to use ``HuggingFace`` and ``OpenAI`` models in EvaDB to answer questions based on videos. In particular, we will first convert the speech component of the video to text using the ``HuggingFace`` model. The generated transcript is stored in a table as a ``text`` column for subsequent analysis. We then use an ``OpenAI`` model to answer questions based on the ``text`` column. 

EvaDB makes it easy to answer questions based on videos using its built-in support for ``HuggingFace`` and ``OpenAI`` models.

.. include:: ../shared/evadb.rst

We will assume that the input ``ukraine_video`` video is loaded into ``EvaDB``. To download the video and load it into ``EvaDB``, see the complete `question answering notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/08-chatgpt.ipynb>`_.


Create Speech Recognition Function
----------------------------------

To create a custom ``SpeechRecognizer`` function based on the popular ``Whisper`` model, use the ``CREATE FUNCTION`` statement. In this query, we leverage EvaDB's built-in support for ``HuggingFace`` models. We only need to specify the ``task`` and the ``model`` parameters in the query to create this function:

.. code-block:: sql

    CREATE FUNCTION SpeechRecognizer 
    TYPE HuggingFace 
        TASK 'automatic-speech-recognition' 
        MODEL 'openai/whisper-base';

.. note::
    
    EvaDB has built-in support for a wide range of :ref:`HuggingFace<hf>` models.

Create ChatGPT Function
------------------------

EvaDB has built-in support for ``ChatGPT`` function from ``OpenAI``. You will need to configure the ``OpenAI`` key in the environment as shown below:

.. code-block:: python

    # Set OpenAI key
    import os
    os.environ["OPENAI_KEY"] = "sk-..."

.. note::
    
    EvaDB has built-in support for a wide range of :ref:`OpenAI<openai>` models. You can also switch to another large language models that runs locally by defining a :ref:`Custom function<udf>`.


    ChatGPT function is a wrapper around OpenAI API call. You can also switch to other LLM models that can run locally.

Convert Speech to Text
----------------------

After registering the ``SpeechRecognizer`` function, we run it over the video to obtain the video's transcript. EvaDB supports direct reference to the ``audio`` component of the video as shown in this query:

.. code-block:: sql

        CREATE TABLE text_summary AS 
        SELECT SpeechRecognizer(audio) 
        FROM ukraine_video; 

Here, the ``SpeechRecognizer`` function is applied on the ``audio`` component of the ``ukraine_video`` video loaded into EvaDB. The output of the ``SpeechRecognizer`` function is stored in the ``text`` column of the ``text_summary`` table.

Here is the query's output ``DataFrame``:

.. code-block:: 

    +-------------------------------------------------------------------------------------------------------------------------+
    |                                                    text_summary.text                                                    |
    +-------------------------------------------------------------------------------------------------------------------------+
    | The war in Ukraine has been on for 415 days. Who is winning it? Not Russia. Certainly not Ukraine. It is the US oil ... |
    +-------------------------------------------------------------------------------------------------------------------------+

Question Answering using ChatGPT
--------------------------------

We next run a EvaQL query that uses the ``ChatGPT`` function on the ``text`` column to answer questions based on the video. The ``text`` column serves as important ``context`` for the large language model. This query checks if the video is related to the war between Ukraine and Russia.

.. code-block:: sql

        SELECT ChatGPT(
            'Is this video summary related to Ukraine russia war', 
            text) 
        FROM text_summary;

Here is the query's output ``DataFrame``:

.. code-block:: 

    +--------------------------------------------------------------------------------------------------------------------------+
    |                                                     chatgpt.response                                                     |
    +--------------------------------------------------------------------------------------------------------------------------+
    | No, the video summary provided does not appear to be related to the Ukraine-Russia war. It seems to be a conversatio ... |
    +--------------------------------------------------------------------------------------------------------------------------+

.. include:: ../shared/nlp.rst

.. include:: ../shared/footer.rst
