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
    print(cursor.query("SHOW FUNCTIONS;").df())


.. autosummary:: 
    :toctree: ./doc
    
    ~evadb.connect
    ~evadb.EvaDBConnection.cursor
    ~evadb.EvaDBCursor.query
    ~evadb.EvaDBQuery.df

.. warning::

    ``cursor.query("...").df()`` constructs and then runs the query to get the output dataframe.

    It is important to call ``df`` to run the actual query and get the output dataframe. ``cursor.query("...")`` only constructs the query. It does not execute the query.
    

.. include:: ../shared/designs/design4.rst