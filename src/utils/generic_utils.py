# coding=utf-8
# Copyright 2018-2020 EVA
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
import importlib
import torch
import uuid
import hashlib
import os
from pathlib import Path

from src.configuration.configuration_manager import ConfigurationManager
from src.utils.logging_manager import LoggingManager, LoggingLevel


def validate_kwargs(kwargs, allowed_kwargs,
                    error_message='Keyword argument not understood:'):
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


def path_to_class(filepath: str, classname: str):
    """
    Convert the class in the path file into an object

    Arguments:
        filepath: absolute path of file
        classname: the name of the imported class

    Returns:
        type: A class for given path
    """
    try:
        abs_path = str(Path(filepath).resolve())
        module_dir, module_file = os.path.split(abs_path)
        module_name, module_ext = os.path.splitext(module_file)
        spec = importlib.util.spec_from_file_location(module_name, abs_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        classobj = getattr(module, classname)
    except Exception as e:
        LoggingManager().log(
            'Failed to import %s from %s\nException: %s'
            % (classname, filepath, e),
            LoggingLevel.WARNING)
    return classobj


def is_gpu_available() -> bool:
    """
    Checks if the system has GPUS available to execute tasks
    Returns:
        [bool] True if system has GPUs, else False
    """
    return torch.cuda.is_available()


def generate_file_path(name: str = '') -> Path:
    """Generates a arbitrary file_path(md5 hash) based on the a random salt
    and name

    Arguments:
        name (str): Input file_name.

    Returns:
        Path: pathlib.Path object

    """
    dataset_location = ConfigurationManager().get_value("core", "location")
    if dataset_location is None:
        LoggingManager().log(
            'Missing location key in eva.yml', LoggingLevel.ERROR)
        raise KeyError('Missing location key in eva.yml')

    dataset_location = Path(dataset_location)
    salt = uuid.uuid4().hex
    file_name = hashlib.md5(salt.encode() + name.encode()).hexdigest()
    path = dataset_location / file_name
    return path.resolve()
