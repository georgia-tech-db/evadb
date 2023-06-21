Basic API
==========

To begin your querying session, get a connection with a cursor to EvaDB using ``connect`` and ``cursor`` function calls:

.. autosummary:: 
    :toctree: ./doc
    
    ~evadb.connect
    ~evadb.EvaDBConnection.cursor

.. code-block:: python

    import evadb

    cursor = evadb.connect().cursor()

You can then use this cursor to run queries:

.. code-block:: python

    ### load the pdfs in a given folder into the "office_data" table
    cursor.load(
        file_regex=f"office_data/*.pdf", format="PDF", table_name="office_data_table"
    ).df()

    ### load a given video into the "youtube_videos" table
    cursor.load("movie.mp4", "youtube_videos", "video").df()

.. warning::

    It is important to call ``df`` to run the actual query and get the result dataframe. EvaDB does lazy query execution to improve performance.

    Calling ``cursor.query("...")`` will only construct and not run the query. Calling ``cursor.query("...").df()`` will both construct and run the query.

EvaDBCursor Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~evadb.EvaDBCursor.load
    ~evadb.EvaDBCursor.drop_table
    ~evadb.EvaDBCursor.table
    ~evadb.EvaDBCursor.query
    ~evadb.EvaDBCursor.create_udf
    ~evadb.EvaDBCursor.drop_udf
    ~evadb.EvaDBCursor.create_vector_index
    ~evadb.EvaDBCursor.drop_index

EvaDBQuery Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~evadb.EvaDBQuery.select
    ~evadb.EvaDBQuery.cross_apply
    ~evadb.EvaDBQuery.filter
    ~evadb.EvaDBQuery.df
    ~evadb.EvaDBQuery.alias
    ~evadb.EvaDBQuery.limit
    ~evadb.EvaDBQuery.order
    ~evadb.EvaDBQuery.show
    ~evadb.EvaDBQuery.sql_query
    ~evadb.EvaDBQuery.execute