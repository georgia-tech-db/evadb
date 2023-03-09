# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import hashlib
import importlib
import inspect
import pickle
import sys
import uuid
from pathlib import Path

from aenum import AutoEnum, unique

from eva.configuration.configuration_manager import ConfigurationManager
from eva.utils.logging_manager import logger


def validate_kwargs(
    kwargs, allowed_kwargs, error_message="Keyword argument not understood:"
):
    """Checks that all keyword arguments are in the set of allowed keys."""
    for kwarg in kwargs:
        if kwarg not in allowed_kwargs:
            raise TypeError(error_message, kwarg)


def str_to_class(class_path: str):
    """
    Convert string representation of a class path to Class

    Arguments:
        class_path (str): absolute path of import

    Returns:
        type: A Class for given path
    """
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def load_udf_class_from_file(filepath, classname=None):
    """
    Load a class from a Python file.

    Args:
        filepath (str): The path to the Python file.
        classname (str, optional): The name of the class to load. If not specified, the function will try to load a class with the same name as the file. Defaults to None.

    Returns:
        The class instance.

    Raises:
        ImportError: If the file can't be imported.
        ValueError: If the class name is not found or there is more than one class in the file.
    """
    module_name = inspect.getmodulename(filepath)
    if module_name is None:
        raise ImportError(f"Couldn't import module from {filepath}")
    module = importlib.import_module(module_name, filepath)

    # Try to load the specified class by name
    if classname:
        if hasattr(module, classname):
            return getattr(module, classname)
        else:
            raise RuntimeError(f"Class {classname} not found in {filepath}")

    # If class name not specified, check if there is only one class in the file
    classes = [obj for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]
    if len(classes) != 1:
        raise RuntimeError(
            f"{filepath} contains multiple classes, please specify the main class by naming the UDF with the same name."
        )
    return classes[0]


def is_gpu_available() -> bool:
    """
    Checks if the system has GPUS available to execute tasks
    Returns:
        [bool] True if system has GPUs, else False
    """
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def generate_file_path(name: str = "") -> Path:
    """Generates a arbitrary file_path(md5 hash) based on the a random salt
    and name

    Arguments:
        name (str): Input file_name.

    Returns:
        Path: pathlib.Path object

    """
    dataset_location = ConfigurationManager().get_value("core", "datasets_dir")
    if dataset_location is None:
        logger.error("Missing dataset location key in eva.yml")
        raise KeyError("Missing datasets_dir key in eva.yml")

    dataset_location = Path(dataset_location)
    dataset_location.mkdir(parents=True, exist_ok=True)

    salt = uuid.uuid4().hex
    file_name = hashlib.md5(salt.encode() + name.encode()).hexdigest()
    path = dataset_location / file_name
    return path.resolve()


def get_size(obj, seen=None):
    """Recursively finds size of objects
    https://goshippo.com/blog/measure-real-size-any-python-object/
    """
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


class PickleSerializer(object):
    @classmethod
    def serialize(cls, data):
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def deserialize(cls, data):
        return pickle.loads(data)


@unique
class EVAEnum(AutoEnum):
    def __str__(self):
        return self.name
