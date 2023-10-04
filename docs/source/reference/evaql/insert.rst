INSERT 
=======

TABLE MyVideo
-------------

MyVideo Table schema

.. code:: text

    CREATE TABLE MyVideo
    (id INTEGER,
    data NDARRAY FLOAT32(ANYDIM));

INSERT INTO TABLE
-----------------

Insert a tuple into a table. If there is an index built on the table, the index will be automatically updated. Currently, we only support index automatic update with FAISS and SQLite data.

.. code:: text

    INSERT INTO MyVideo (id, data) VALUES 
        (1,
            [[[40, 40, 40] , [40, 40, 40]],
             [[40, 40, 40] , [40, 40, 40]]]);
