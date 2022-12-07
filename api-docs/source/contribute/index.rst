Contributing
----

We welcome all kinds of contributions to EVA.

-  `Code reviews <https://github.com/georgia-tech-db/eva/pulls>`_
-  `Improving documentation <https://github.com/georgia-tech-db/eva/tree/master/api-docs>`_
-  `Tutorials and applications <https://github.com/georgia-tech-db/eva/tree/master/tutorials>`_
-  New features

Setting up the Development Environment
=====

First, you will need to checkout the repository from GitHub and build EVA from
the source. Follow the following instructions to build EVA locally. We recommend using a virtual environment and the pip package manager. 

EVA requires JAVA 11 for generating the ANTLR-based EVAQL parser.

.. code-block:: bash

   git clone https://github.com/georgia-tech-db/eva.git && cd eva
   python3 -m venv test_eva_db                            # to create a virtual environment
   . test_eva_db/bin/activate
   pip install --upgrade pip
   sudo -E apt install -y openjdk-11-jdk openjdk-11-jre   # to install JAVA
   sh script/antlr4/generate_parser.sh                    # to generate the EVA parser
   pip install -e ".[dev]"
   bash script/test/test.sh                               # to run the test suite

For developers using an M1 Mac, here are some pointers for installing JAVA and to resolve multi-threading issues:

.. code-block:: bash      

   brew install openjdk@11                         # to install openjdk 11
   export JAVA_HOME="/opt/homebrew/opt/openjdk@11" # add this command in ~/.zshrc or ~/.bashrc
   export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES  # to resolve multi-threading issues in macOS
   
After you have installed the package locally, you can make changes in the code base and examine their impact.

.. code-block:: bash

   pip install .         # reinstall EVA package to include local changes 
   pkill -9 eva_server   # kill running EVA server (if any)
   eva_server&           # launch EVA server with newly installed package


Testing
====

Check if your local changes broke any unit or integration tests by running the following script:

.. code-block:: bash

   bash script/test/test.sh

If you want to run a specific test file, use the following command.

.. code-block:: bash

   python -m pytest test/integration_tests/test_select_executor.py

Use the following command to run a specific test case within a specific test
file.

.. code-block:: bash

   python -m pytest test/integration_tests/test_select_executor.py -k 'test_should_load_and_select_in_table'

Submitting a Contribution
====

Follow the following steps to contribute to EVA:

-  Merge the most recent changes from the master branch

.. code-block:: bash

       git remote add origin git@github.com:georgia-tech-db/eva.git
       git pull . origin/master

-  Run the `test script <#testing>`__ to ensure that all the test cases pass.
-  If you are adding a new EVAQL command, add an illustrative example usage in 
   the `documentation <https://github.com/georgia-tech-db/eva/tree/master/api-docs>`_.
- Run the following command to ensure that code is properly formatted.

.. code-block:: python

      python script/formatting/formatter.py 

Code Style
====

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


Troubleshooting
====

If the test suite fails with a `PermissionDenied` exception, update the `path_prefix` attribute under the `storage` section in the EVA configuration file (``~/.eva/eva.yml``) to a directory where you have write privileges.
