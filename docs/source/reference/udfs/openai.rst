OpenAI Models
=====================

This section provides an overview of how you can use OpenAI models in EVA.


Chat Completion UDFs
--------------------

To create a chat completion UDF in EVA, use the following SQL command:

.. code-block:: sql

    CREATE UDF IF NOT EXISTS OpenAIChatCompletion
    IMPL 'eva/udfs/openai_chat_completion_udf.py'
    'model' 'gpt-3.5-turbo'

EVA supports the following models for chat completion task:

- "gpt-4"
- "gpt-4-0314"
- "gpt-4-32k"
- "gpt-4-32k-0314"
- "gpt-3.5-turbo"
- "gpt-3.5-turbo-0301"

The chat completion UDF can be composed in interesting ways with other UDFs. Please refer to the following notebook <add link to notebook> for an example of combining chat completion task with caption extraction and video summarization models from Hugging Face and feeding it to chat completion to ask questions about the results.

<Add Image>
<Add Queries>