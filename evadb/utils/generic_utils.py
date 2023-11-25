# coding=utf-8
# Copyright 2018-2023 EvaDB
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
import os
import pickle
import shutil
import sys
import uuid
from pathlib import Path
from typing import Iterator, List
from urllib.parse import urlparse

from aenum import AutoEnum, unique

from evadb.configuration.constants import EvaDB_INSTALLATION_DIR
from evadb.utils.logging_manager import logger


def validate_kwargs(
    kwargs,
    allowed_keys: List[str],
    required_keys: List[str],
    error_message="Keyword argument not understood:",
):
    """Checks that all keyword arguments are in the set of allowed keys."""
    if required_keys is None:
        required_keys = allowed_keys
    for kwarg in kwargs:
        if kwarg not in allowed_keys:
            raise TypeError(error_message, kwarg)

    missing_keys = [key for key in required_keys if key not in kwargs]
    assert len(missing_keys) == 0, f"Missing required keys, {missing_keys}"


def str_to_class(class_path: str):
    """
    Convert string representation of a class path to Class

    Arguments:
        class_path (str): absolute path of import

    Returns:
        type: A Class for given path
    """
    assert class_path is not None, "Class path is not found"
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


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
    except ModuleNotFoundError as e:
        err_msg = f"ModuleNotFoundError : Couldn't load function from {filepath} : {str(e)}. Not able to load the code provided in the file {abs_path}. Please ensure that the file contains the implementation code for the function."
        raise ModuleNotFoundError(err_msg)
    except ImportError as e:
        # ImportError in the case when we are able to find the file but not able to load the module
        err_msg = f"ImportError : Couldn't load function from {filepath} : {str(e)}. Please ensure that all the correct packages are installed correctly."
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
        return getattr(module, classname)

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


def get_gpu_count() -> int:
    """
    Check number of GPUs through Torch.
    """
    try:
        import torch

        return torch.cuda.device_count()
    except ImportError:
        return 0


def generate_file_path(dataset_location: str, name: str = "") -> Path:
    """Generates a arbitrary file_path(md5 hash) based on the a random salt
    and name

    Arguments:
        dataset_location(str): parent directory where a file needs to be created
        name (str): Input file_name.

    Returns:
        Path: pathlib.Path object

    """
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


def rebatch(it: Iterator, batch_mem_size: int = 30000000) -> Iterator:
    """
    Utility function to rebatch the rows
    Args:
        it (Iterator): an iterator for rows, every row is a dictionary
        batch_mem_size (int): the maximum batch memory size
    Yields:
        data_batch (List): a list of rows, every row is a dictionary
    """
    data_batch = []
    row_size = None
    for row in it:
        data_batch.append(row)
        if row_size is None:
            row_size = get_size(data_batch)
        if len(data_batch) * row_size >= batch_mem_size:
            yield data_batch
            data_batch = []
    if data_batch:
        yield data_batch


def get_str_hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def get_file_checksum(fname: str) -> str:
    """Compute checksum of the file contents

    Args:
        fname (str): file path

    Returns:
        str: hash string representing the checksum of the file content
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def parse_config_yml():
    """
    Parses the 'evadb.yml' file and returns the config object.
    """
    import yaml

    f = open(Path(EvaDB_INSTALLATION_DIR) / "evadb.yml", "r+")
    config_obj = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    return config_obj


def is_postgres_uri(db_uri):
    """
    Determines if the db_uri is that of postgres.

    Args:
        db_uri (str) : db_uri to parse
    """
    parsed_uri = urlparse(db_uri)
    return parsed_uri.scheme == "postgres" or parsed_uri.scheme == "postgresql"


class PickleSerializer(object):
    @classmethod
    def serialize(cls, data):
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def deserialize(cls, data):
        return pickle.loads(data)


@unique
class EvaDBEnum(AutoEnum):
    def __str__(self):
        return self.name


def remove_directory_contents(dir_path):
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}. Reason: {str(e)}")


def find_nearest_word(word, word_list):
    from thefuzz import process

    nearest_word_and_score = process.extractOne(word, word_list)
    nearest_word = nearest_word_and_score[0]

    return nearest_word


##############################
## TRY TO IMPORT PACKAGES
##############################


def try_to_import_ray():
    try:
        import ray  # noqa: F401
        from ray.util.queue import Queue  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import ray python package.
                Please install it with `pip install ray`."""
        )


def try_to_import_statsforecast():
    try:
        from statsforecast import StatsForecast  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import StatsForecast python package.
                Please install it with `pip install statsforecast`."""
        )


def try_to_import_neuralforecast():
    try:
        from neuralforecast import NeuralForecast  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import NeuralForecast python package.
                Please install it with `pip install neuralforecast`."""
        )


def is_ray_available() -> bool:
    try:
        try_to_import_ray()
        return True
    except ValueError:  # noqa: E722
        return False


def is_ray_enabled_and_installed(ray_enabled: bool) -> bool:
    ray_installed = is_ray_available()
    return ray_enabled and ray_installed


##############################
## MODEL TRAIN FRAMEWORK
##############################


def try_to_import_ludwig():
    try:
        import ludwig  # noqa: F401
        from ludwig.automl import auto_train  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import ludwig.
                Please install it with `pip install evadb[ludwig]`."""
        )


def is_ludwig_available() -> bool:
    try:
        try_to_import_ludwig()
        return True
    except ValueError:  # noqa: E722
        return False


def is_forecast_available() -> bool:
    try:
        try_to_import_statsforecast()
        try_to_import_neuralforecast()
        return True
    except ValueError:  # noqa: E722
        return False


def try_to_import_flaml_automl():
    try:
        import flaml  # noqa: F401
        from flaml import AutoML  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import Flaml AutML.
                Please install it with `pip install "flaml[automl]"`."""
        )


def is_flaml_automl_available() -> bool:
    try:
        try_to_import_flaml_automl()
        return True
    except ValueError:  # noqa: E722
        return False


##############################
## VISION
##############################


def try_to_import_pillow():
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import pillow python package.
                Please install it with `pip install pillow`."""
        )


def try_to_import_torch():
    try:
        import torch  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import torch python package.
                Please install them with `pip install torch`."""
        )


def try_to_import_torchvision():
    try:
        import torchvision  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import torchvision python package.
                Please install them with `pip install torchvision`."""
        )


def try_to_import_cv2():
    try:
        import cv2  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import cv2 python package.
                Please install it with `pip install opencv-python`."""
        )


def try_to_import_timm():
    try:
        import timm  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import timm python package.
                Please install them with `pip install timm`."""
        )


def try_to_import_kornia():
    try:
        import kornia  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import kornia python package.
                Please install it with `pip install kornia`."""
        )


def try_to_import_decord():
    try:
        import decord  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import decord python package.
                Please install it with `pip install eva-decord`."""
        )


def try_to_import_ultralytics():
    try:
        import ultralytics  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import ultralytics python package.
                Please install it with `pip install ultralytics`."""
        )


def try_to_import_norfair():
    try:
        import norfair  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import norfair python package.
                Please install it with `pip install norfair`."""
        )


##############################
## DOCUMENT
##############################


def try_to_import_transformers():
    try:
        import transformers  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import transformers python package.
                Please install it with `pip install transformers`."""
        )


def try_to_import_facenet_pytorch():
    try:
        import facenet_pytorch  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import facenet_pytorch python package.
                Please install it with `pip install facenet-pytorch`."""
        )


def try_to_import_openai():
    try:
        import openai  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import openai python package.
                Please install them with `pip install openai`."""
        )


def try_to_import_langchain():
    try:
        import langchain  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import langchain package.
                Please install it with `pip install langchain`."""
        )


##############################
## VECTOR STORES
##############################


def try_to_import_faiss():
    try:
        import faiss  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import faiss python package.
                Please install it with `pip install faiss-cpu` or `pip install faiss-gpu`."""
        )


def try_to_import_qdrant_client():
    try:
        import qdrant_client  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import qdrant_client python package.
                Please install it with `pip install qdrant_client`."""
        )


def try_to_import_pinecone_client():
    try:
        import pinecone  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import pinecone_client python package.
                Please install it with 'pip install pinecone_client`."""
        )


def try_to_import_chromadb_client():
    try:
        import chromadb  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import chromadb python package.
                Please install it with 'pip install chromadb`."""
        )


def try_to_import_weaviate_client():
    try:
        import weaviate  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import weaviate python package.
                Please install it with 'pip install weaviate-client`."""
        )


def try_to_import_milvus_client():
    try:
        import pymilvus  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import pymilvus python package.
                Please install it with 'pip install pymilvus`."""
        )


def is_qdrant_available() -> bool:
    try:
        try_to_import_qdrant_client()
        return True
    except ValueError:  # noqa: E722
        return False


def is_pinecone_available() -> bool:
    try:
        try_to_import_pinecone_client()
        return True
    except ValueError:  # noqa: E722
        return False


def is_chromadb_available() -> bool:
    try:
        try_to_import_chromadb_client()
        return True
    except ValueError:  # noqa: E722
        return False


def is_weaviate_available() -> bool:
    try:
        try_to_import_weaviate_client()
        return True
    except ValueError:  # noqa: E722
        return False


def is_milvus_available() -> bool:
    try:
        try_to_import_milvus_client()
        return True
    except ValueError:
        return False


##############################
## UTILS
##############################


def try_to_import_moto():
    try:
        import boto3  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import boto3 python package.
                Please install it with `pip install moto[s3]`."""
        )


def try_to_import_fitz():
    try:
        import fitz  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import fitz python package.
                Please install it with `pip install pymupdfs`."""
        )


def string_comparison_case_insensitive(string_1, string_2) -> bool:
    """
    Case insensitive string comparison for two strings which gives
    a bool response whether the strings are the same or not

    Arguments:
        string_1 (str)
        string_2 (str)

    Returns:
        True/False (bool): Returns True if the strings are same, false otherwise
    """

    # Does not make sense in case of null strings
    if string_1 is None or string_2 is None:
        return False

    return string_1.lower() == string_2.lower()


def try_to_import_replicate():
    try:
        import replicate  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import replicate python package.
                Please install it with `pip install replicate`."""
        )


def is_replicate_available():
    try:
        try_to_import_replicate()
        return True
    except ValueError:
        return False
