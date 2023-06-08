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





EvaDBConnection Interface
-------------------------

.. autosummary::
    :toctree: ./doc
    
    ~evadb.EvaDBConnection.cursor


EvaDBCursor Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~evadb.EvaDBCursor.connect
    ~evadb.EvaDBCursor.load
    ~evadb.EvaDBCursor.query
    ~evadb.EvaDBCursor.table
    ~evadb.EvaDBCursor.create_udf
    ~evadb.EvaDBCursor.create_vector_index
    ~evadb.EvaDBCursor.df

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
