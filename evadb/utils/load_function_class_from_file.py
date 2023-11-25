from evadb.functions.helpers.udf import UserDefinedFunction


import importlib
import inspect
from pathlib import Path


def load_function_class_from_file(filepath, classname=None):
    """
    Load a class from a Python file. If the classname is not specified, the function will check if there is only one class in the file and load that. If there are multiple classes, it will raise an error.

    Args:
        filepath (str): The path to the Python file.
        classname (str, optional): The name of the class to load. If not specified, the function will try to load a class with the same name as the file. Defaults to None.

    Returns:
        The class instance.

    Raises:
        ImportError: If the module cannot be loaded.
        FileNotFoundError: If the file cannot be found.
        RuntimeError: Any othe type of runtime error.
    """
    try:
        abs_path = Path(filepath).resolve()
        spec = importlib.util.spec_from_file_location(abs_path.stem, abs_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except ImportError as e:
        # ImportError in the case when we are able to find the file but not able to load the module
        err_msg = f"ImportError : Couldn't load function from {filepath} : {str(e)}. Not able to load the code provided in the file {abs_path}. Please ensure that the file contains the implementation code for the function."
        raise ImportError(err_msg)
    except FileNotFoundError as e:
        # FileNotFoundError in the case when we are not able to find the file at all at the path.
        err_msg = f"FileNotFoundError : Couldn't load function from {filepath} : {str(e)}. This might be because the function implementation file does not exist. Please ensure the file exists at {abs_path}"
        raise FileNotFoundError(err_msg)
    except Exception as e:
        # Default exception, we don't know what exactly went wrong so we just output the error message
        err_msg = f"Couldn't load function from {filepath} : {str(e)}."
        raise RuntimeError(err_msg)

    # Try to load the specified class by name
    if classname and hasattr(module, classname):
        obj = getattr(module, classname)
        if not inspect.isclass(obj):
            return UserDefinedFunction(obj)
        return obj

    # If class name not specified, check if there is only one class in the file
    classes = [
        obj
        for _, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    ]
    if len(classes) != 1:
        raise ImportError(
            f"{filepath} contains {len(classes)} classes, please specify the correct class to load by naming the function with the same name in the CREATE query."
        )

    if not inspect.isclass(classes[0]):
        return UserDefinedFunction(classes[0])

    return classes[0]