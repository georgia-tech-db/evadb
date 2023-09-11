PostgreSQL
==========

The connection to PostgreSQL is based on the `psycopg2 <https://pypi.org/project/psycopg2/>`_ library.

Dependency
----------

* psycopg2


Parameters
----------

Required:

* `user` is the database user.
* `password` is the database password.
* `host` is the host name, IP address, or URL.
* `port` is the port used to make TCP/IP connection.
* `database` is the database name.


Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE postgres_data WITH ENGINE = 'postgres', PARAMETERS = {
        "user": "eva", 
        "password": "password",
        "host": "localhost",
        "port": "5432", 
        "database": "evadb"
   };

