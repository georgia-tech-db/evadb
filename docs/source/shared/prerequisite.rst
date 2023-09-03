Prerequisites
-------------

To follow along, you will need to set up a local instance of EvaDB via `pip <../overview/getting-started>`_. 

We will assume that you have a ``PostgreSQL`` database server running locally that contains the data needed for analysis. Follow these instructions to install `PostgreSQL <https://www.postgresql.org/download/>`_.

Connect to EvaDB
----------------

After installing EvaDB, use the following Python code to establish a connection and obtain a ``cursor`` for running ``EvaQL`` queries.

.. code-block:: python

    import evadb
    cursor = evadb.connect().cursor()

Connect EvaDB to PostgreSQL Database Server
-------------------------------------------

EvaDB lets you connect to your favorite databases, data warehouses, data lakes, etc., via the ``CREATE DATABASE`` statement. In this query, we connect EvaDB to an existing ``PostgreSQL`` server:

.. tab-set::
    
    .. tab-item:: Python

        .. code-block:: python

            params = {
                "user": "eva",
                "password": "password",
                "host": "localhost",
                "port": "5432",
                "database": "evadb",
            }
            query = f"CREATE DATABASE postgres_data 
                      WITH ENGINE = 'postgres', 
                      PARAMETERS = {params};"
            cursor.query(query).df()

    .. tab-item:: SQL 

        .. code-block:: sql

            CREATE DATABASE postgres_data 
            WITH ENGINE = 'postgres', 
            PARAMETERS = {
                "user": "eva",
                "password": "password",
                "host": "localhost",
                "port": "5432",
                "database": "evadb"
            }
