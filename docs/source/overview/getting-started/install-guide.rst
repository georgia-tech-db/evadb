.. _installation guide:

Installation Guide
==================

EvaDB provides couple different installation options to allow easy extension to rich functionalities. 

Use pip
-------

EvaDB supports Python (versions >= 3.8). We recommend installing with `pip` within an `isolated virtual environment <https://docs.python-guide.org/dev/virtualenvs/>`_.

.. code-block:: bash

    python -m venv evadb-venv
    source evadb-venv/bin/activate
    pip install --upgrade pip
    pip install evadb

Install additional packages
---------------------------

* `evadb[vision]` for vision dependencies. With vision dependencies, we can run queries to do image classification, object detection, and emotion analysis workloads, etc.
* `evadb[document]` for LLM dependencies. With LLM dependencies, we can leverage the capability of LLM to summarize or do question answering for documents.
* `evadb[qdrant]` for embedding-based similarity search.
* `evadb[ludwig]` for model training and finetuning.
* `evadb[ray]` for distributed execution on ray.

Install from source
-------------------

.. code-block:: bash

   git clone https://github.com/georgia-tech-db/evadb.git
   cd evadb
   pip install -e .

.. note::

   Check :ref:`Contribution Guide<contributing>` for more details.

Run your first SQL query in EvaDB
----------------------------------

To run SQL query in EvaDB, we need to first create a `cursor` object. The following query lists all the builtin user-defined functions. 

.. code-block:: python

   import evdb
   cursor = evadb.connect().cursor()
   print(cursor.query("SHOW UDFS;").df())

.. note::

   Check :ref:`Python APIs<python-api>` for connection and cursor-related documentation.

