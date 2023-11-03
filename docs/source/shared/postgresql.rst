Connect EvaDB to PostgreSQL Database Server
-------------------------------------------

We will assume that you have a :ref:`PostgreSQL<postgresql>` database running locally that contains the data needed for analysis. Follow these instructions to install `PostgreSQL <https://www.postgresql.org/download/>`_. 

.. note::
    If find it challenging to install the ``PostgreSQL`` database on your machine, here is an alternative for quick prototyping. 
    
    You can use an embedded :ref:`SQLite<sqlite>` database. If you go with the ``sqlite`` database, alter the SQL commands in this tutorial to use the ``sqlite`` engine and the ``evadb.db`` SQLite database file as explained in the :ref:`SQLite<sqlite>` page.

EvaDB lets you connect to your favorite databases, data warehouses, data lakes, etc., via the ``CREATE DATABASE`` statement. In this query, we connect EvaDB to an existing ``PostgreSQL`` server:

.. code-block::

    CREATE DATABASE postgres_data 
    WITH ENGINE = 'postgres', 
    PARAMETERS = {
        "user": "eva",
        "password": "password",
        "host": "localhost",
        "port": "5432",
        "database": "evadb"
    }
