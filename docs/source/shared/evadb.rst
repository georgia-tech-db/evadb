Prerequisites
-------------

To follow along, you will need to set up a local instance of EvaDB via :ref:`pip<getting-started>`. 

Connect to EvaDB
----------------

After installing EvaDB, use the following Python code to establish a connection and obtain a ``cursor`` for running ``EvaQL`` queries.

.. code-block:: python

    import evadb
    cursor = evadb.connect().cursor()
