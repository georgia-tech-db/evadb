Development Environment
=====================================================

Checkout Latest EvaDB
---------------------

First, you will need to checkout the repository from GitHub and build EvaDB from the source. 

.. code-block:: bash

   git clone https://github.com/georgia-tech-db/evadb.git && cd evadb

Build EvaDB Locally
-------------------

Follow the following instructions to build EvaDB locally. We recommend using a virtual environment and the pip package manager. 

.. code-block:: bash

   python3 -m venv test_evadb_venv
   source test_evadb_venv/bin/activate
   pip install --upgrade pip
   pip install -e ".[dev]"
   
After installing the package locally, you can make changes and run the test cases to check their impact.

.. note::
   
   EvaDB provides multiple installation options for extending its functionalities. 
   Please see :ref:`installation options` for all options.

Other options can be installed with the ``dev`` environment.

.. code-block:: bash
   
   pip install -e ".[dev,ludwig]"
