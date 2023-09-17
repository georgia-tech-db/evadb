MariaDB
==========

The connection to MariaDB is based on the `mariadb <https://mariadb-corporation.github.io/mariadb-connector-python/>`_ library.

Dependency
----------

* mariadb


Parameters
----------

Required:

* `user` is the username corresponding to the database
* `password` is the password for the above username for the database
* `database` is the database name
* `host` is the host name, IP address or the URL
* `port` is the port used to make the TCP/IP connection.


Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE mariadb_data WITH ENGINE = 'mariadb', PARAMETERS = {
        "user" : "eva",
        "password": "password",
        "host": "127.0.0.1".
        "port": "7567",
        "database": "evadb"
   };

