.. _openai:

OpenAI Models
=====================

This section provides an overview of how you can use OpenAI models in EvaDB.


Chat Completion Functions
-------------------------

To create a chat completion function in EvaDB, use the following SQL command:

.. code-block:: sql

    CREATE FUNCTION IF NOT EXISTS OpenAIChatCompletion
    IMPL 'evadb/functions/openai_chat_completion_function.py'
    MODEL 'gpt-3.5-turbo'

EvaDB supports the following models for chat completion task:

- "gpt-4"
- "gpt-4-0314"
- "gpt-4-32k"
- "gpt-4-32k-0314"
- "gpt-3.5-turbo"
- "gpt-3.5-turbo-0301"

The chat completion function can be composed in interesting ways with other functions. Please check the  `Google Colab <https://colab.research.google.com/github/georgia-tech-db/evadb/blob/master/tutorials/08-chatgpt.ipynb>`_ for an example of combining chat completion task with caption extraction and video summarization models from Hugging Face and feeding it to chat completion to ask questions about the results.
