### Documentation on Debugging Eva:

Using a debugger in the visual studio code, is one of the optimal ways of debugging your User Defined Function(UDF). This tutorial gives a detailed step-by-step process of using a debugger with Eva. This tutorial is python-specific. However, a similar debugging process can be followed for other languages and frameworks as well.

## Pre-requisites:
Python should be installed and its environment should be defined in the VS Code. If not pre-installed, use the extensions section to install python and set-up the environment. Follow the [offical instructions](https://realpython.com/python-development-visual-studio-code).


## STEP 1: Installing and setting-up debugger on Visual Studio Code
----------------------------------------------------------------

The debug option in Visual Studio Code is as follows:

The debug icon when pressed will give you the option to create a launch.json file.


While creating the JSON file, you will be prompted to select the environment to be used. Select the python environment from the command Palette at the top. If the python environment cannot be seen in the drop-down menu, try installing the python extension, and repeat the process.

Once you select the python environment, a `launch.json` file will be created with the default configurations set to debug a simple .py file.

More configurations can further be added to the file, to modify the environment variables or to debug an entire folder or workspace directory.

Use the following approach for debugging the eva set-up:

```
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
            "env": {"PYTHONPATH": "${workspaceRoot}"}
        }

    ]
}
```


You can modify the fields of the above JSON file as follows:

   `name`:  It is the reader-friendly name to appear in the Debug launch configuration dropdown.

   `type`: The type of debugger to use for this launch configuration.

   `program`: The executable or file to run when launching the debugger. In the above example, test_integration.py will be executed by the debugger.

   `env`: Here you specify the environment variables. In the above example, the path for the conda environment for Eva has been specified.


Using these configurations, the debugger can be executed both locally as well as on the remote server.