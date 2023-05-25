Troubleshoot
=============

cannot install certain dependencies
----

fix #1
~~~~

Make ensure that local python version >= 3.7.0


eva_server fails
----

fix #1
~~~~

Check if a process is already running on the target port (port_number). If so, terminate the process with process_id running on the port:

.. code-block:: bash

    sudo lsof -i :<port_number>
    kill -9 <process_id>

fix #2
~~~~

Remove eva's running directory. To do this, open a new terminal and run

.. code-block:: bash

    rm -rf .eva

eva_client stuck at some query
----

fix #1
~~~~

Check if the query ends with a semi-colon.

fix #2
~~~~

If a query runs a complex process (such as image recognition) on many image frames, the query is expected to take long.

eva_client LOAD query fails because image/video path does not exist
----

fix #1
~~~~

Make sure the path actually exists. If so:
1. Remove eva's running directory. To do this, open a new terminal and run

.. code-block:: bash

    rm -rf .eva

2. Re-install dependencies. To do this, in a terminal, run

.. code-block:: bash

    pip install --upgrade pip
    pip install -e ".[dev]"
    pip install .

