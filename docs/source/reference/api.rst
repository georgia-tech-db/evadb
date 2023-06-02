Python API
=================

Database Interface
------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::
    :toctree: ./doc

    ~db.EVAConnection.create_vector_index
    ~db.EVAConnection.cursor
    ~db.EVAConnection.df
    ~db.EVAConnection.load
    ~db.EVAConnection.sql
    ~db.EVAConnection.table
    ~db.EVAConnection.query

Table Interface
------------

.. currentmodule:: eva.interfaces.relational

.. autosummary::
    :toctree: ./doc
    
    ~relation.EVARelation.alias
    ~relation.EVARelation.cross_apply
    ~relation.EVARelation.df
    ~relation.EVARelation.execute
    ~relation.EVARelation.filter
    ~relation.EVARelation.limit
    ~relation.EVARelation.order
    ~relation.EVARelation.select
    ~relation.EVARelation.show
    ~relation.EVARelation.sql_query