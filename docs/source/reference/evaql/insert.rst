INSERT 
=======

TABLE MyVideo
-------------

MyVideo Table schema

.. code:: mysql

    CREATE TABLE MyVideo
    (id INTEGER,
    data NDARRAY FLOAT32(ANYDIM));

INSERT INTO TABLE
-----

Insert a tuple into a table.

.. code:: mysql

    INSERT INTO MyVideo (id, data) VALUES 
        (1,
            [[[40, 40, 40] , [40, 40, 40]],
             [[40, 40, 40] , [40, 40, 40]]]);