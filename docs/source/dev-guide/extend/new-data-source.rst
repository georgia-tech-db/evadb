.. _add-data-source:

Structured Data Source Integration
==================================
This document details steps involved in adding a new structured data source integration in EvaDB.


Example Data Source Integration In EvaDB
----------------------------------------

- `PostgreSQL <https://github.com/georgia-tech-db/evadb/tree/master/evadb/third_party/databases/postgres>`_


Create Data Source Handler
--------------------------

1. Create a new directory at `evadb/third_party/databases/ <https://github.com/georgia-tech-db/evadb/tree/master/evadb/third_party/databases>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   The directory name is also the engine name used in the `CREATE DATABASE mydb_source WITH ENGINE = "..."`. In this document, we use **mydb** as the example data source we want to integrate in EvaDB.

The directory should contain three files:

- __init__.py
- requirements.txt
- mydb_handler.py

The *__init__.py* can contain copyright information. The *requirements.txt* contains the extra python libraries that need to be installed via pip for the mydb data source. 

.. note:: 

   EvaDB will only install a data source's specific dependency libraries when a connection to the data source is created by the user via, e.g., `CREATE DATABASE mydb_source WITH ENGINE = "mydb";`.

2. Implement the data source handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In *mydb_handler.py*, you need to implement the `DBHandler` declared at `evadb/third_party/databases/types.py <https://github.com/georgia-tech-db/evadb/blob/master/evadb/third_party/databases/types.py>`_. There are 7 functions that you need to implement:

.. code:: python

   class MydbHandler(DBHandler):

        def __init__(self, name: str, **kwargs):
                ...
        def connect(self):
                ...
        def disconnect(self):
                ...
        def check_connection(self) -> DBHandlerStatus:
                ...
        def get_tables(self) -> DBHandlerResponse:
                ...
        def get_columns(self, table_name: str) -> DBHandlerResponse:
                ...
        def execute_native_query(self, query_string: str) -> DBHandlerResponse:
                ...

The *get_tables* should retrieve the list of tables from the data source. The *get_columns* should retrieve the columns of a specified table from the database. The *execute_native_query* specifies how to execute the query through the data source's engine. For more details, please check the function signature and documentation at `evadb/third_party/databases/types.py <https://github.com/georgia-tech-db/evadb/blob/master/evadb/third_party/databases/types.py>`_.

You can get the data source's configuration parameters from `__init__(self, name: str, **kwargs)`. Below is an example:

.. code:: python

   def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")
        self.user = kwargs.get("user")
        self.password = kwargs.get("password")

.. note::

   Those parameters will be specified when the user creates a connection to the data source: `CREATE DATABASE mydb_source WITH ENGINE = "mydb", PARAMETERS = {"host": "localhost", "port": "5432", "user": "eva", "password": "password"};`.

You can check the PostgreSQL's handler example at `evadb/third_party/databases/postgres/postgres_handler.py <https://github.com/georgia-tech-db/evadb/blob/master/evadb/third_party/databases/postgres/postgres_handler.py>`_ for ideas.


Register the Data Source Handler
--------------------------------

Add your created data source handler in `get_database_handler` function at `evadb/third_party/databases/interface.py <https://github.com/georgia-tech-db/evadb/blob/master/evadb/third_party/databases/interface.py>`_. Below is an example of registering the created mydb data source:

.. code:: python

   ...
   elif engine == "mydb":
        return mod.MydbHandler(engine, **kwargs)
   ...

Add the Data Source in Documentation
------------------------------------

Add your new data source into :ref:`databases` section for reference.

- Create ``mydb.rst`` under `evadb/docs/source/reference/databases <https://github.com/georgia-tech-db/evadb/tree/staging/docs/source/reference/databases>`_ directory. You can refer to the existing documentation under the directory for example information to be covered in ``mydb.rst``.
- Update ``source/reference/databases/postgres`` in `evadb/docs/_toc.yml <https://github.com/georgia-tech-db/evadb/blob/staging/docs/_toc.yml>`_.
