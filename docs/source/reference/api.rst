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





EvaDBDBConnection Interface
-------------------------

.. autosummary::
    :toctree: ./doc
    
    ~evadb.EvaDBDBConnection.cursor


EvaDBDBCursor Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~evadb.EvaDBDBCursor.connect
    ~evadb.EvaDBDBCursor.load
    ~evadb.EvaDBDBCursor.query
    ~evadb.EvaDBDBCursor.table
    ~evadb.EvaDBDBCursor.create_udf
    ~evadb.EvaDBDBCursor.create_vector_index
    ~evadb.EvaDBDBCursor.df

EvaDBDBQuery Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~evadb.EvaDBDBQuery.select
    ~evadb.EvaDBDBQuery.cross_apply
    ~evadb.EvaDBDBQuery.filter
    ~evadb.EvaDBDBQuery.df
    ~evadb.EvaDBDBQuery.alias
    ~evadb.EvaDBDBQuery.limit
    ~evadb.EvaDBDBQuery.order
    ~evadb.EvaDBDBQuery.show
    ~evadb.EvaDBDBQuery.sql_query