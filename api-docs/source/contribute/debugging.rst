..  _guide-debugging:

Documentation on Debugging Eva:
===============================

Using a debugger in the visual studio code, is one of the optimal ways of debugging your User Defined Function(UDF). This tutorial gives a detailed step-by-step process of using a debugger with Eva. This tutorial is python-specific. However, a similar debugging process can be followed for other languages and frameworks as well.

Pre-requisites:
--------------
Python should be installed and its environment should be defined in the VS Code. If not pre-installed, use the extensions section to install python and set-up the environment.
A detailed link for the same is as follows:

https://realpython.com/python-development-visual-studio-code


STEP 1: Installing and setting-up debugger on Visual Studio Code
----------------------------------------------------------------

The debug option in Visual Studio Code is as follows:

.. image:: images/run.png

The debug icon when pressed will give you the option to create a launch.json file.

.. image:: images/launch-configuration.png

While creating the JSON file, you will be prompted to select the environment to be used. Select the python environment from the command Palette at the top. If the python environment can’t be seen in the drop-down menu, try installing the python extension, and repeat the process.

.. image:: images/debug-environments.png

Once you select the python environment, a launch.json file will be created with the default configurations set to debug a simple .py file.

More configurations can further be added to the file, to modify the environment variables or to debug an entire folder or workspace directory.

Use the following approach for debugging the eva set-up:

{

    "version": "0.2.0",
    "configurations": [

       {
            "name": "Python: test_pytorch.py",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/test/integration_tests/test_pytorch.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {"PYTHONPATH": "${workspaceRoot}",
                    "PYSPARK_PYTHON" : "/nethome/username/miniconda/envs/eva/bin/python",
                    "PYSPARK_DRIVER_PYTHON": "/nethome/username/miniconda/envs/eva/bin/python"}
        }

    ]
}



You can modify the fields of the above JSON file as follows:

   #. “name”:  It is the reader-friendly name to appear in the Debug launch configuration dropdown.


   #. “type”: The type of debugger to use for this launch configuration.


   #. “program”: The executable or file to run when launching the debugger. In the above example, test_integration.py will be executed by the debugger.


   #. “env”: Here you specify the environment variables. In the above example, the path for the conda environment for Eva has been specified.


Using these configurations, the debugger can be executed both locally as well as on the remote server.

Step 2: Using the Debugger for Eva
-----------------------------------

Before starting the debugger, ensure that the Eva Conda environment is activated.
Also, start the Eva server, by running python eva.py.

To start using the debugger, set breakpoints in the file you want to debug.

.. image:: images/breakpoints.png

Now you can go to the debug menu, and you will see a play button at the top specifying the configurations you have mentioned in the launch.json file.

Choose the appropriate configuration, and press the play button to start debugging.

The debugger will automatically start running the Eva framework and will stop at the point where you have applied the breakpoint.

Once the debugger stops at the breakpoint, consider the following:

You can see the variables at each stage, the call stack as well as the list of breakpoints on the left-hand panel of the visual studio code.

.. image:: images/debug-session.png

Use the debug actions to start executing the program step-by-step from the breakpoint. For this purpose, the following debug actions have been provided:


   #. Continue / Pause F5: To run your program starting from the breakpoint.


   #. Step Over F10:  To step over a specific function.


   #. Step Into F11: To go inside a specific function and check its internal execution.


   #. Step Out F11: To step out of a function.


   #. Restart F5: To restart the debugging.


   #. Stop F5: To stop the debugging.

.. image:: images/toolbar.png
