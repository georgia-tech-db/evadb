Prerequisites
-------------

To follow along, you will need to set up a local instance of EvaDB via `pip <getting-started>`. 

We will assume that you have a `PostgreSQL` database server running locally that contains the data needed for analysis. Follow these instructions to install `Postgres <https://www.postgresql.org/download/>`.

Connect to EvaDB
----------------

After you have installed EvaDB, use the following Python code to establish a connection and obtain a cursor that is used for running EvaQL queries.

.. code-block:: python

    import evadb
    cursor = evadb.connect().cursor()

Connect EvaDB to an Existing Database Server
--------------------------------------------

EvaDB lets you connect to your favorite databases, data warehouses, data lakes, etc., via the `CREATE DATABASE` statement. In this query, we connect to a `PostgreSQL` server.

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
