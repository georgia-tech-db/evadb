Contributing
----------------

We welcome all kinds of contributions to EvaDB.

-  `Code reviews <https://github.com/georgia-tech-db/evadb/pulls>`_
-  `Improving documentation <https://github.com/georgia-tech-db/evadb/tree/master/docs>`_
-  `Tutorials and applications <https://github.com/georgia-tech-db/evadb/tree/master/tutorials>`_
-  `New features <new-command.html>`__

Setting up the Development Environment
=====================================================

First, you will need to checkout the repository from GitHub and build EvaDB from the source. 

.. code-block:: bash

   git clone https://github.com/georgia-tech-db/evadb.git && cd evadb

Follow the following instructions to build EvaDB locally. We recommend using a virtual environment and the pip package manager. 

.. code-block:: bash

   python3 -m venv test_evadb_venv
   source test_evadb_venv/bin/activate
   pip install --upgrade pip
   pip install -e ".[dev]"
   
After installing the package locally, you can make changes and run the test cases to check their impact.

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

   PYTHONPATH="." python -m pytest test/integration_tests/test_select_executor.py

Use the following command to run a specific test case within a specific test file.

.. code-block:: bash

   PYTHONPATH="." python -m pytest test/integration_tests/test_select_executor.py -k 'test_should_load_and_select_in_table'

Submitting a PR
============================

For every open PR, we only run unit tests and short integration test to facilitate merging features quickly. 
Once PR passes those tests, it will be merged into our `staging` branch for more comprehensive integration, version, and
application tests. 

Follow the following steps to contribute to EvaDB:

-  Merge the most recent changes from the `staging` branch

.. code-block:: bash

       git remote add origin git@github.com:georgia-tech-db/evadb.git
       git pull . origin/staging

-  Run the `test script <#testing>`__ to ensure that all the test cases pass.
-  If you are adding a new EvaDB command, add an illustrative example usage in 
   the `documentation <https://github.com/georgia-tech-db/evadb/tree/master/docs>`_.
- Run the following command to ensure that code is properly formatted.

.. code-block:: python

      python script/formatting/formatter.py 

Code Style
============

We use the `black <https://github.com/psf/black>`__ code style for
formatting the Python code. For docstrings and documentation, we use
`Google Pydoc format <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`__.

.. code-block:: python

   def function_with_types_in_docstring(param1, param2) -> bool:
       """Example function with types documented in the docstring.

       Additional explanatory text can be added in paragraphs.

       Args:
           param1 (int): The first parameter.
           param2 (str): The second parameter.

       Returns:
           bool: The return value. True for success, False otherwise.

Architecture Diagram
========================

.. image:: ../../images/evadb/evadb-arch.png
   :width: 1200

Troubleshooting
====================

If the test suite fails with a `PermissionDenied` exception, update the `path_prefix` attribute under the `storage` section in the EvaDB configuration file (``~/.evadb/evadb.yml``) to a directory where you have write privileges.
