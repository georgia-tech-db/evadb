.. _python-api:

Python API
==========

To begin a querying session in EvaDB, obtain a connection with a cursor using ``connect`` and ``cursor`` functions. After getting the cursor, you can run queries with the ``query`` function in this manner:

.. code-block:: python

    # Import the EvaDB package
    import evadb

    # Connect to EvaDB and get a database cursor for running queries
    cursor = evadb.connect().cursor()

    # List all the built-in functions in EvaDB
    print(cursor.query("SHOW UDFS;").df())


.. autosummary:: 
    :toctree: ./doc
    
    ~evadb.connect
    ~evadb.EvaDBConnection.cursor
    ~evadb.EvaDBCursor.query
    ~evadb.EvaDBCursor.df

.. warning::

    It is important to call ``df`` to run the actual query and get the output dataframe.

    ``cursor.query("...")`` only construct the query and not run the query. ``cursor.query("...").df()`` will both construct and run the query.

