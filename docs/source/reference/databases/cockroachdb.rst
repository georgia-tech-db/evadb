CockroachDB
==========

The connection to CockroackDB is based on the `psycopg2 <https://pypi.org/project/psycopg2/>`_ library.

Dependency
----------

* psycopg2 



Parameters
----------

Required:

* `user` is the database user.
* `password` is the database password.
* `host` is the host name or IP address.
* `port` is the port used to make TCP/IP connection to the CockroachDB server.
* `database` is the database name.


Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE cockroachdb_data WITH ENGINE = 'cockroachdb', PARAMETERS = {
        "user": "eva", 
        "password": "password",
        "host": "localhost",
        "port": "26257", 
        "database": "evadb"
   };
