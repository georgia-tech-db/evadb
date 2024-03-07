.. _gemini:

Gemini Models
=====================

This section provides an overview of how you can use Gemini models in EvaDB.


Chat Completion Functions
-------------------------

To create a chat completion function in EvaDB, use the following SQL command:

.. code-block:: sql

    CREATE FUNCTION IF NOT EXISTS GeminiChatCompletion
    IMPL 'evadb/functions/gemini.py'
    MODEL 'gemini-pro'

EvaDB supports the following models for chat completion task:

- "gemini-pro"

The chat completion function can be composed in interesting ways with other functions. Gemini can be used similar to the `ChatGPT` function as shown in `Google Colab <https://colab.research.google.com/github/georgia-tech-db/evadb/blob/master/tutorials/08-chatgpt.ipynb>`_. as an example of combining chat completion task with caption extraction and video summarization models from Hugging Face and feeding it to chat completion to ask questions about the results.
