Basic API
==========

To begin your querying session, get a connection to the EvaDB using ``connect``:

.. code-block:: python

    import eva

    from eva import connect
    conn = connect()

You can then use this connection to run queries:

.. code-block:: python

    conn.load("online_video.mp4", "youtube_video", "video").execute()
    conn.query("CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;").execute()

.. warning::

    It is important to call ``execute`` to run the actual query. 
    
    EvaDB uses a lazy query execution technique to improve performance.
    Calling ``conn.query("...")`` will only construct and not run the query. Calling ``conn.query("...").execute()`` will both construct and run the query.

EVADBConnection Interface
-----------------------

.. currentmodule:: eva.interfaces.relational


.. autosummary::
    :toctree: ./doc
    
    ~db.EVADBConnection.cursor

EVADBQuery Interface
---------------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::
    :toctree: ./doc

    ~relation.EVADBQuery.select
    ~relation.EVADBQuery.execute
    ~relation.EVADBQuery.cross_apply
    ~relation.EVADBQuery.filter
    ~relation.EVADBQuery.df

Advanced API
=============

EVADBConnection Interface
-----------------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::
    :toctree: ./doc

    ~db.EVADBConnection.create_udf
    ~db.EVADBConnection.create_vector_index
    ~db.EVADBConnection.df

EVADBQuery Interface
---------------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::
    :toctree: ./doc

    ~relation.EVADBQuery.alias
    ~relation.EVADBQuery.limit
    ~relation.EVADBQuery.order
    ~relation.EVADBQuery.show
    ~relation.EVADBQuery.sql_query