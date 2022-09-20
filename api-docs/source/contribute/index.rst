Contributing
~~~~~~~~~~~~

We welcome all kinds of contributions to EVA.

-  New features
-  Code reviewing of PR
-  Documentation
-  Tutorials and Applications

Setting up the development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To hack on EVA, you need to checkout the repository and build EVA from
the source. Follow the following instructions to build EVA and test your
changes locally. We recommend using a virtual environment and the pip
package manager. EVA requires JAVA 11 for generating the parser.

::

   git clone https://github.com/georgia-tech-db/eva.git && cd eva
   python3 -m venv env38                                  # to create a virtual environment
   . env38/bin/activate
   pip install --upgrade pip
   sudo -E apt install -y openjdk-11-jdk openjdk-11-jre   # to install JAVA
   sh script/antlr4/generate_parser.sh                    # to generate the EVA parser
   pip install -e ".[dev]"
   bash script/test/test.sh                               # to run the test suite


For developers using an M1 Mac, here are some pointers for installing JAVA and to resolve multi-threading issues:

::      

   brew install openjdk@11                         # to install openjdk 11
   export JAVA_HOME="/opt/homebrew/opt/openjdk@11" # add this command in ~/.zshrc or ~/.bashrc
   export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES  # to resolve multi-threading issues in macOS
   
      
Testing
^^^^^^^

Before merging the PR, the code must pass all the unit test cases. You
can use the following script to run all the test cases locally.

::

   bash script/test/test.sh

If you want to run a specific test file, use the following command.

::

   python -m pytest test/integration_tests/test_select_executor.py

Use the following command to run a specific test case within a test
file.

::

   python -m pytest test/integration_tests/test_select_executor.py -k 'test_should_load_and_select_in_table'

Troubleshooting
^^^^^^^^^^^^^^^

If the tests fail with `PermissionDenied` exceptions, change the `path_prefix` attribute
under `storage` in ``~/.eva/eva.yml`` to a directory you have write privileges in.

Submitting a contribution
^^^^^^^^^^^^^^^^^^^^^^^^^

Follow the following steps to contribute to EVA:

-  Merge the most recent changes from the master branch

::

       git remote add origin git@github.com:georgia-tech-db/eva.git
       git pull . origin/master

-  Run the `test script <#testing>`__ to ensure all the test cases pass.
-  Run the ``setup_git_hooks.sh`` to add a git pre-push hook so that it
   runs the linter before pushing any changes.
-  If you are adding a new SQL command, please add the example usage to
   the documentation.

Code Style
^^^^^^^^^^

We use the `black <https://github.com/psf/black>`__ code style for
formatting our python code. For docstrings and documentation, we use
`Google pydoc
format <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`__.

::

   def function_with_types_in_docstring(param1, param2) -> bool:
       """Example function with types documented in the docstring.

       Additional explanatory text can be added in paragraphs.

       Args:
           param1 (int): The first parameter.
           param2 (str): The second parameter.

       Returns:
           bool: The return value. True for success, False otherwise.

Lint and Formatting
'''''''''''''''''''

Before merging, the PR must pass the code formatting and linting test
case. On your local machine, run the following script to auto-format
using ``black``

::

   python script/formatting/formatter.py 
