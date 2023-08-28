Installation Guide
==================

EvaDB provides couple different installation options to allow easy extension to rich functionalities. 

Default
-------

By Default, EvaDB installs only the minimal requirements.

.. code-block::

    pip install evadb

Vision Capability
-----------------

You can install EvaDB with the vision extension. 
With vision extension, you can run queries to do image classification, object detection, and emotion analysis workloads, etc.

.. code-block::

    pip install evadb[vision]

Documents Summarization with LLM
--------------------------------

You can also use EvaDB to leverage the capability of LLM to summarize or do question answering for documents.

.. code-block::

    pip install evadb[document]

Additional Vector Index
-----------------------

EvaDB installs ``faiss`` vector index by default, but users can also install other index library such as ``qdrant`` for similarity search feature.

.. code-block::

    pip install evadb[qdrant]

Training or Finetuning Model
----------------------------

Instead of using existing models for only inference, you can also train a customized function inside EvaDB with the ``ludwig`` extension.

.. code-block::

    pip install evadb[ludwig]

Better Performance and Scalability
----------------------------------

EvaDB also allows users to improve the query performance by using ``ray`` to parallelize queries.

.. code-block::

    pip install evadb[ray]