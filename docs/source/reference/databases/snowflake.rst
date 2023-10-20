Snowflake
==========

The connection to Snowflake is based on the `snowflake-connector-python <https://pypi.org/project/snowflake-connector-python/>`_ library.

Dependency
----------

* snowflake-connector-python

Parameters
----------

Required:

* `user` is the database user.
* `password` is the snowflake account password.
* `database` is the database name.
* `warehouse` is the snowflake warehouse name.
* `account` is the snowflake account number ( can be found in the url ).
* `schema` is the schema name.


.. warning:: 

     Provide the parameters of an already running ``Snowflake`` Data Warehouse. EvaDB only connects to an existing ``Snowflake`` Data Warehouse.

Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE snowflake_data WITH ENGINE = 'snowflake', PARAMETERS = {
        "user": "<username>",
        "password": "<my_password>"
        "account": "<account_number>",
        "database": "EVADB",
        "warehouse":  "COMPUTE_WH",
        "schema": "SAMPLE_DATA"
   };

.. warning::

    | In Snowflake Terminology, ``Database`` and ``Schema`` refer to the following.
    | A database is a logical grouping of schemas. Each database belongs to a single Snowflake account.
    | A schema is a logical grouping of database objects (tables, views, etc.). Each schema belongs to a single database.

