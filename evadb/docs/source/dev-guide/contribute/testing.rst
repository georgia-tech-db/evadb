Testing
=========

Check if your local changes broke any unit or integration tests by running the following script:

.. code-block:: bash

   bash script/test/test.sh

By default, it will run the full test suite. You can also run subset of test suites.

.. code-block:: bash

   # Unit tests.
   bash script/test/test.sh -m UNIT

   # Integration tests.
   bash script/test/test.sh -m "SHORT INTEGRATION" 
   bash script/test/test.sh -m "LONG INTEGRATION" 

If you want to run a specific test file, use the following command.

.. code-block:: bash

   PYTHONPATH="." python -m pytest test/integration_tests/long/test_select_executor.py

Use the following command to run a specific test case within a specific test file.

.. code-block:: bash

   PYTHONPATH="." python -m pytest test/integration_tests/long/test_select_executor.py -k 'test_should_load_and_select_in_table'