Basic API
==========

To begin your querying session, get a connection to the EvaDB using ``connect``:

.. autosummary:: 
    :toctree: ./doc
    
    ~evadb.connect

.. code-block:: python

    from evadb import connect
    conn = connect()

You can then use this connection to run queries:

.. code-block:: python

    conn.load("online_video.mp4", "youtube_video", "video").df()
    conn.query("CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;").df()

.. warning::

    It is important to call ``df`` to run the actual query. 
    
    EvaDB uses a lazy query execution technique to improve performance.
    Calling ``conn.query("...")`` will only construct and not run the query. Calling ``conn.query("...").df()`` will both construct and run the query.





EVADBConnection Interface
-------------------------

.. autosummary::
    :toctree: ./doc
    
    ~evadb.EVADBConnection.cursor


EVADBCursor Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~evadb.EVADBCursor.connect
    ~evadb.EVADBCursor.load
    ~evadb.EVADBCursor.query
    ~evadb.EVADBCursor.table
    ~evadb.EVADBCursor.create_udf
    ~evadb.EVADBCursor.create_vector_index
    ~evadb.EVADBCursor.df

EVADBQuery Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~evadb.EVADBQuery.select
    ~evadb.EVADBQuery.cross_apply
    ~evadb.EVADBQuery.filter
    ~evadb.EVADBQuery.df
    ~evadb.EVADBQuery.alias
    ~evadb.EVADBQuery.limit
    ~evadb.EVADBQuery.order
    ~evadb.EVADBQuery.show
    ~evadb.EVADBQuery.sql_query