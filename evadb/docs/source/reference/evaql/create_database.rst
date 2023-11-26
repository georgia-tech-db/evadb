CREATE DATABASE
===============

.. _create-database:

The CREATE DATABASE statement allows us to connect to an external structured data store in EvaDB.

.. code:: text

   CREATE DATABASE [database_connection]
        WITH ENGINE = [database_engine],
        PARAMETERS = [key_value_parameters];

* [database_connection] is the name of the database connection. `[database_connection].[table_name]` will be used as table name to compose SQL queries in EvaDB.
* [database_engine] is the supported database engine. Check :ref:`supported data sources<databases>` for all engine and their available configuration parameters.
* [key_value_parameters] is a list of key-value pairs as arguments to establish a connection.


Examples
~~~~~~~~

.. code:: text

   CREATE DATABASE postgres_data WITH ENGINE = 'postgres', PARAMETERS = {
        "user": "eva", 
        "password": "password",
        "host": "localhost",
        "port": "5432", 
        "database": "evadb"
   };
