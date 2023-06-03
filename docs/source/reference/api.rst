Basic API
==========

To begin your querying session, get a connection to the EvaDB using ``connect``:

.. code-block:: python
    import evadb

    from eva.interfaces.relational.db import EVAConnection, connect
    conn = connect()

You can then use this connection to run queries:

.. code-block:: python
    conn.load("online_video.mp4", "youtube_video", "video").execute()
    conn.query("CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;").execute()

.. warning::
    It is important to call ``execute`` to run the actual query. EvaDB uses a lazy query execution technique to improve user productivity. So, merely calling ``conn.query("...")`` will not run the query. Only ``conn.query("...").execute()`` will run the query.

EVAConnection Interface
-----------------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::

    ~db.EVAConnection.connect
    ~db.EVAConnection.load
    ~db.EVAConnection.query
    ~db.EVAConnection.table

EVARelation Interface
---------------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::
    
    ~relation.EVARelation.select
    ~relation.EVARelation.execute
    ~relation.EVARelation.cross_apply
    ~relation.EVARelation.filter
    ~relation.EVARelation.df

Advanced API
=============

EVAConnection Interface
-----------------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::

    ~db.EVAConnection.create_vector_index
    ~db.EVAConnection.df

EVARelation Interface
---------------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::

    ~relation.EVARelation.alias
    ~relation.EVARelation.limit
    ~relation.EVARelation.order
    ~relation.EVARelation.show
    ~relation.EVARelation.sql_query