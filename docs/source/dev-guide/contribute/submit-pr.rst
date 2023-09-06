Submitting a PR
============================

For every open PR, we only run unit tests and short integration test to facilitate merging features quickly. 
Once PR passes those tests, it will be merged into our ``staging`` branch for more comprehensive integration, version, and
application tests. 

Follow the following steps to contribute to EvaDB.

Sync with ``Staging`` Branch
----------------------------

Merge the most recent changes from the ``staging`` branch

.. code-block:: bash

       git remote add origin git@github.com:georgia-tech-db/evadb.git
       git pull . origin/staging

Testing
-----------------

Run the :doc:`test script <./testing>` to ensure that all the test cases pass.

Documentation
-------------

If you are adding a new EvaDB command, add an illustrative example usage in the 
`documentation <https://github.com/georgia-tech-db/evadb/tree/master/docs>`_.

Formatting
----------

Run the following command to ensure that code is properly formatted.

.. code-block:: python

      python script/formatting/formatter.py 
