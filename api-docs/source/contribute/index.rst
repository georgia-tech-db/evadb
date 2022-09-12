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
package manager. EVA requires JAVA 8 for generating the parser.

::

   git clone https://github.com/georgia-tech-db/eva.git && cd eva
   python3 -m venv env38                                # to create a virtual environment
   . env38/bin/activate
   pip install --upgrade pip
   sudo -E apt install -y openjdk-11-jdk openjdk-11-jre   # to install JAVA
   sh script/antlr4/generate_parser.sh                  # to generate the EVA parser
   pip install -e ".[dev]"

For M1 Mac users, we recommend using the following instructions to safely
setup EVA (dev) on your local machine.

1.  Install Java 11 using homebrew.

   `brew install openjdk@11`
2.  If you have existing versions of Java or if `java -version` doesn't point to the homebrew
version of Java you have just installed, run the following command:

   `export JAVA_HOME="/opt/homebrew/opt/openjdk@11"`

   You can also add the above command inside `./zshrc` to permanently set the path to Java.
3. Run the following command to resolve multithreading issues in macOS:

   `export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

   WARNING: Do not add this command inside `./zshrc` as not all programs require this. Either run
   this command every time or setup a shell script to do so for you.
4. Open `setup.py` and edit the line `opencv-python==4.5.1.48` to `opencv-python>=4.5.1.58`.
5. Install as per instructions shared above (except for the Java installation part)
6. Run `bash script/test/test.sh` to verify everything is working correctly.

Common issues with M1 Mac Installation:
-  If while installing, an error is thrown regarding no version of opencv-python being available
   (or)
   If there are build errors (eg. numpy build errors) while installing opencv-pythonm do the following:

   Replace the version in `setup.py` from `opencv-python==<version_no>` to `opencv-python>=<version_no>`.
-  If you get errors related to `from .cv2 import *`, it is likely that there are conflicting versions
of `opencv-python` causing this problem. Running the following should most likely resolve the issue:

   `pip install --upgrade opencv-python`

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
