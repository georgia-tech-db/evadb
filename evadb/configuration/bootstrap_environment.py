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
import importlib.resources as importlib_resources
import logging
from pathlib import Path
from typing import Union

import yaml

from evadb.configuration.constants import (
    CACHE_DIR,
    DB_DEFAULT_NAME,
    INDEX_DIR,
    MODEL_DIR,
    S3_DOWNLOAD_DIR,
    TMP_DIR,
    UDF_DIR,
    EvaDB_CONFIG_FILE,
    EvaDB_DATASET_DIR,
)
from evadb.utils.generic_utils import parse_config_yml
from evadb.utils.logging_manager import logger as evadb_logger


def get_base_config(evadb_installation_dir: Path) -> Path:
    """
    Get path to .evadb.yml source path.
    """
    # if evadb package is installed in environment
    if importlib_resources.is_resource("evadb", EvaDB_CONFIG_FILE):
        with importlib_resources.path("evadb", EvaDB_CONFIG_FILE) as yml_path:
            return yml_path
    else:
        # For local dev environments without package installed
        return evadb_installation_dir / EvaDB_CONFIG_FILE


def get_default_db_uri(evadb_dir: Path):
    """
    Get the default database uri.

    Arguments:
        evadb_dir: path to evadb database directory
    """
    config_obj = parse_config_yml()
    if config_obj["core"]["catalog_database_uri"]:
        return config_obj["core"]["catalog_database_uri"]
    else:
        # Default to sqlite.
        return f"sqlite:///{evadb_dir.resolve()}/{DB_DEFAULT_NAME}"


def bootstrap_environment(evadb_dir: Path, evadb_installation_dir: Path):
    """
    Populates necessary configuration for EvaDB to be able to run.

    Arguments:
        evadb_dir: path to evadb database directory
        evadb_installation_dir: path to evadb package
    """

    default_config_path = get_base_config(evadb_installation_dir).resolve()

    # creates necessary directories
    config_default_dict = create_directories_and_get_default_config_values(
        Path(evadb_dir), Path(evadb_installation_dir)
    )

    assert evadb_dir.exists(), f"{evadb_dir} does not exist"
    assert evadb_installation_dir.exists(), f"{evadb_installation_dir} does not exist"
    config_obj = {}
    with default_config_path.open("r") as yml_file:
        config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)
    config_obj = merge_dict_of_dicts(config_default_dict, config_obj)
    mode = config_obj["core"]["mode"]

    # set logger to appropriate level (debug or release)
    level = logging.WARN if mode == "release" else logging.DEBUG
    evadb_logger.setLevel(level)
    evadb_logger.debug(f"Setting logging level to: {str(level)}")

    return config_obj


def create_directories_and_get_default_config_values(
    evadb_dir: Path, evadb_installation_dir: Path, category: str = None, key: str = None
) -> Union[dict, str]:
    default_install_dir = evadb_installation_dir
    dataset_location = evadb_dir / EvaDB_DATASET_DIR
    index_dir = evadb_dir / INDEX_DIR
    cache_dir = evadb_dir / CACHE_DIR
    s3_dir = evadb_dir / S3_DOWNLOAD_DIR
    tmp_dir = evadb_dir / TMP_DIR
    udf_dir = evadb_dir / UDF_DIR
    model_dir = evadb_dir / MODEL_DIR

    if not evadb_dir.exists():
        evadb_dir.mkdir(parents=True, exist_ok=True)
    if not dataset_location.exists():
        dataset_location.mkdir(parents=True, exist_ok=True)
    if not index_dir.exists():
        index_dir.mkdir(parents=True, exist_ok=True)
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
    if not s3_dir.exists():
        s3_dir.mkdir(parents=True, exist_ok=True)
    if not tmp_dir.exists():
        tmp_dir.mkdir(parents=True, exist_ok=True)
    if not udf_dir.exists():
        udf_dir.mkdir(parents=True, exist_ok=True)
    if not model_dir.exists():
        model_dir.mkdir(parents=True, exist_ok=True)

    config_obj = {}
    config_obj["core"] = {}
    config_obj["storage"] = {}
    config_obj["core"]["evadb_installation_dir"] = str(default_install_dir.resolve())
    config_obj["core"]["datasets_dir"] = str(dataset_location.resolve())
    config_obj["core"]["catalog_database_uri"] = get_default_db_uri(evadb_dir)
    config_obj["storage"]["index_dir"] = str(index_dir.resolve())
    config_obj["storage"]["cache_dir"] = str(cache_dir.resolve())
    config_obj["storage"]["s3_download_dir"] = str(s3_dir.resolve())
    config_obj["storage"]["tmp_dir"] = str(tmp_dir.resolve())
    config_obj["storage"]["udf_dir"] = str(udf_dir.resolve())
    config_obj["storage"]["model_dir"] = str(model_dir.resolve())
    if category and key:
        return config_obj.get(category, {}).get(key, None)
    elif category:
        return config_obj.get(category, {})
    return config_obj


def merge_dict_of_dicts(dict1, dict2):
    """In case of conflict override with dict2"""
    merged_dict = dict1.copy()

    for key, value in dict2.items():
        # Overwrite only if some value is specified.
        if value:
            if (
                key in merged_dict
                and isinstance(merged_dict[key], dict)
                and isinstance(value, dict)
            ):
                merged_dict[key] = merge_dict_of_dicts(merged_dict[key], value)
            else:
                merged_dict[key] = value

    return merged_dict
