Clickhouse
==========

The connection to Clickhouse is based on the `clickhouse-sqlalchemy <https://pypi.org/project/clickhouse-sqlalchemy/>`_ library.

Dependency
----------

* clickhouse-sqlalchemy



Parameters
----------

Required:

* `user` is the database user.
* `password` is the database password.
* `host` is the host name or IP address.
* `port` is the port used to make TCP/IP connection to the Clickhouse server.
* `database` is the database name.
* `protocol` (optional) Default- `native`. Its supported values are `http` and `https`.


Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE clickhouse_data WITH ENGINE = 'clickhouse', PARAMETERS = {
        "user": "eva", 
        "password": "password",
        "host": "localhost",
        "port": "5432", 
        "database": "evadb"
   };
