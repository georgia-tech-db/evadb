Python Client API
=================

DB Interface
-------------

.. currentmodule:: eva.interfaces.relational


EVAConnection APIs
~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: ./doc

    ~db.EVAConnection.create_vector_index
    ~db.EVAConnection.cursor
    ~db.EVAConnection.df
    ~db.EVAConnection.load
    ~db.EVAConnection.create_udf
    ~db.EVAConnection.sql
    ~db.EVAConnection.table
    ~db.EVAConnection.query


EVACursor APIs
~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: ./doc

    ~db.EVACursor.create_vector_index
    ~db.EVACursor.df
    ~db.EVACursor.fetch_all_async
    ~db.EVACursor.load
    ~db.EVACursor.sql
    ~db.EVACursor.table
    ~db.EVACursor.create_udf
    ~db.EVACursor.query