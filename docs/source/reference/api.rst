Basic API
==========

To begin your querying session, get a connection to the EvaDB using ``connect``:

.. autosummary:: 
    :toctree: ./doc
    
    ~eva.connect

.. code-block:: python

    from eva import connect
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
    
    ~eva.EVADBConnection.cursor


EVADBCursor Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~eva.EVADBCursor.connect
    ~eva.EVADBCursor.load
    ~eva.EVADBCursor.query
    ~eva.EVADBCursor.table
    ~eva.EVADBCursor.create_udf
    ~eva.EVADBCursor.create_vector_index
    ~eva.EVADBCursor.df

EVADBQuery Interface
---------------------

.. autosummary::
    :toctree: ./doc

    ~eva.EVADBQuery.select
    ~eva.EVADBQuery.cross_apply
    ~eva.EVADBQuery.filter
    ~eva.EVADBQuery.df
    ~eva.EVADBQuery.alias
    ~eva.EVADBQuery.limit
    ~eva.EVADBQuery.order
    ~eva.EVADBQuery.show
    ~eva.EVADBQuery.sql_query