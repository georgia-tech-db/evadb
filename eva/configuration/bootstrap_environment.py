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
import importlib.resources as importlib_resources
import logging
import shutil
from pathlib import Path
from typing import Union

import yaml

from eva.configuration.constants import (
    CACHE_DIR,
    DB_DEFAULT_NAME,
    EVA_CONFIG_FILE,
    EVA_DATASET_DIR,
    INDEX_DIR,
    S3_DOWNLOAD_DIR,
    TMP_DIR,
    UDF_DIR,
)
from eva.utils.logging_manager import logger as eva_logger


def get_base_config(eva_installation_dir: Path) -> Path:
    """
    Get path to .eva.yml source path.
    This file will be copied to user's .eva directory.
    """
    # if eva package is installed into environment
    if importlib_resources.is_resource("eva", EVA_CONFIG_FILE):
        with importlib_resources.path("eva", EVA_CONFIG_FILE) as yml_path:
            return yml_path
    else:
        # For local dev environments without package installed
        return eva_installation_dir / EVA_CONFIG_FILE


def get_default_db_uri(eva_db_dir: Path):
    return f"sqlite:///{eva_db_dir.resolve()}/{DB_DEFAULT_NAME}"


def bootstrap_environment(eva_db_dir: Path, eva_installation_dir: Path):
    """
    Populates necessary configuration for EVA to be able to run.

    Arguments:
        eva_db_dir: path to eva database directory
        eva_installation_dir: path to eva module
    """

    config_file_path = eva_db_dir / EVA_CONFIG_FILE

    # creates necessary directories
    config_default_dict = create_directories_and_get_default_config_values(
        Path(eva_db_dir), Path(eva_installation_dir)
    )

    assert eva_db_dir.exists(), f"{eva_db_dir} does not exist"
    assert eva_installation_dir.exists(), f"{eva_installation_dir} does not exist"

    # copy eva.yml into config path
    if not config_file_path.exists():
        default_config_path = get_base_config(eva_installation_dir).resolve()
        shutil.copy(str(default_config_path.resolve()), str(eva_db_dir.resolve()))

    # Update eva.yml with user specific paths
    with config_file_path.open("r+") as yml_file:
        config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)

        if config_obj is None:
            raise ValueError(f"Invalid yml file at {config_file_path}")

        config_obj = merge_dict_of_dicts(config_obj, config_default_dict)
        mode = config_obj["core"]["mode"]
        yml_file.seek(0)
        yml_file.write(yaml.dump(config_obj))
        yml_file.truncate()

    # set logger to appropriate level (debug or release)
    level = logging.WARN if mode == "release" else logging.DEBUG
    eva_logger.setLevel(level)
    eva_logger.debug(f"Setting logging level to: {str(level)}")


def create_directories_and_get_default_config_values(
    eva_db_dir: Path, eva_installation_dir: Path, category: str = None, key: str = None
) -> Union[dict, str]:
    default_install_dir = eva_installation_dir
    dataset_location = eva_db_dir / EVA_DATASET_DIR
    index_dir = eva_db_dir / INDEX_DIR
    cache_dir = eva_db_dir / CACHE_DIR
    s3_dir = eva_db_dir / S3_DOWNLOAD_DIR
    tmp_dir = eva_db_dir / TMP_DIR
    udf_dir = eva_db_dir / UDF_DIR

    if not eva_db_dir.exists():
        eva_db_dir.mkdir(parents=True, exist_ok=True)
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

    config_obj = {}
    config_obj["core"] = {}
    config_obj["storage"] = {}
    config_obj["core"]["eva_installation_dir"] = str(default_install_dir.resolve())
    config_obj["core"]["datasets_dir"] = str(dataset_location.resolve())
    config_obj["core"]["catalog_database_uri"] = get_default_db_uri(eva_db_dir)
    config_obj["storage"]["index_dir"] = str(index_dir.resolve())
    config_obj["storage"]["cache_dir"] = str(cache_dir.resolve())
    config_obj["storage"]["s3_download_dir"] = str(s3_dir.resolve())
    config_obj["storage"]["tmp_dir"] = str(tmp_dir.resolve())
    config_obj["storage"]["udf_dir"] = str(udf_dir.resolve())
    if category and key:
        return config_obj.get(category, {}).get(key, None)
    elif category:
        return config_obj.get(category, {})
    return config_obj


def merge_dict_of_dicts(dict1, dict2):
    """In case of conflict override with dict2"""
    merged_dict = dict1.copy()

    for key, value in dict2.items():
        if (
            key in merged_dict
            and isinstance(merged_dict[key], dict)
            and isinstance(value, dict)
        ):
            merged_dict[key] = merge_dict_of_dicts(merged_dict[key], value)
        else:
            merged_dict[key] = value

    return merged_dict
