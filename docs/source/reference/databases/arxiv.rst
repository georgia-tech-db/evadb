Arxiv
==========

The connection to Arxiv is based on the `Arxiv <https://github.com/lukasschwab/arxiv.py>`_ library.

Dependency
----------

* Arxiv


Parameters
----------

Required:

* ``query`` is the search query in the Arxiv repository. For example, Nuclear Physics.
* ``max_results`` is the max number of results to display. For example, 10.

Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE arxiv_data WITH ENGINE = 'arxiv', PARAMETERS = {
        "query": "Nuclear Physics",
        "max_results": "10"
   };

Supported Tables
----------------

* ``search_results``: Lists the relevant articles in the arxiv repository. Check `table_column_info.py <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/third_party/databases/arxiv/table_column_info.py>`_ for all the available columns in the table.

.. code-block:: sql

   SELECT * FROM arxiv_data.search_results;

Here is the query output:

.. code-block:: 

    +---------------------------------------------------+-----+---------------------------------------------+
    |                             search_results.title  | ... |                          search_results.doi |
    |---------------------------------------------------|-----|---------------------------------------------|
    | Nuclear Symmetry Energy Extracted from Laborat... | ... |               10.1080/10619127.2017.1388681 |
    | Neutrino astrophysics and its connections to n... | ... |             10.1088/1742-6596/1056/1/012060 |
    |                                               ... | ... |                                         ... |
    +---------------------------------------------------+-----+---------------------------------------------+

.. note::

   Looking for another table from Arxiv? You can add a table mapping in `arxiv_handler.py <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/third_party/databases/arxiv/arxiv_handler.py>`_, or simply raise a `Feature Request <https://github.com/georgia-tech-db/evadb/issues/new/choose>`_.
