MySQL
==========

The connection to MySQL is based on the `mysql-connector-python <https://pypi.org/project/mysql-connector-python/>`_ library.

Dependency
----------

* mysql-connector-python


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

   CREATE DATABASE mysql_data WITH ENGINE = 'mysql', PARAMETERS = {
        "user": "eva", 
        "password": "password",
        "host": "localhost",
        "port": "5432", 
        "database": "evadb"
   };

