Python Client API
=================

DB Interface
-------------

.. currentmodule:: eva.interfaces.relational


EVAConnection APIs
~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: ./doc

    ~db.EVAConnection.cursor
    ~db.EVAConnection.load
    ~db.EVAConnection.table
    ~db.EVAConnection.query


EVACursor APIs
~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: ./doc

    ~db.EVACursor.fetch_all_async
    ~db.EVACursor.load
    ~db.EVACursor.table
    ~db.EVACursor.query