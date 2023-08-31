.. _sql-use:

USE
===

The USE statement allows us to run arbitary native queries in the connected database.

.. code:: mysql

   USE [database_connection] { [native_query] };

* `database_connection` is an external database connection instanced by the `CREATE DATABASE statement`.
* `native_query` is an arbitary SQL query supprted by the `database_connection`. 

.. warning::

   Currently EvaDB only supports single query in one USE statement. The native_query should not end with semicolon.

Examples
--------

.. code:: mysql

   USE postgres_data {
     DROP TABLE IF EXISTS food_review
   };
        
   USE postgres_data {
     CREATE TABLE food_review (name VARCHAR(10), review VARCHAR(1000))
   };

   USE postgres_data {
     INSERT INTO food_review (name, review) VALUES ('Customer 1', 'I ordered fried rice but it is too salty.')
   };


