Hackernews
==========

The connection to Hackernews is based on the `Algolia Hackernews <https://hn.algolia.com/api>`_ API.

Dependency
----------

* requests


Parameters
----------

Required:

* ``query`` is the search query for getting the results.

Optional:

* ``tags`` is the tag used for filtering the query results. Check `available tags <https://hn.algolia.com/api>`_ to see a list of available filter tags.

Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE hackernews_data WITH ENGINE = 'hackernews', PARAMETERS = {
        "query": "EVADB",
        "tags": "story"
   };

Supported Tables
----------------

* ``search_results``: Lists the search query results. Check `table_column_info.py <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/third_party/databases/hackernews/table_column_info.py>`_ for all the available columns in the table.

.. code-block:: sql

   SELECT * FROM hackernews_data.search_results LIMIT 3;

.. note::

   Looking for another table from Hackernews? Please raise a `Feature Request <https://github.com/georgia-tech-db/evadb/issues/new/choose>`_.
