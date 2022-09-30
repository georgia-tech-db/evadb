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

import yaml

from eva.configuration.constants import (
    DB_DEFAULT_URI,
    EVA_CONFIG_FILE,
    EVA_DATASET_DIR,
    EVA_DEFAULT_DIR,
    EVA_UPLOAD_DIR,
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


def bootstrap_environment(eva_config_dir: Path, eva_installation_dir: Path):
    """
    Populates necessary configuration for EVA to be able to run.

    Arguments:
        eva_config_dir: path to user's .eva dir
        default location ~/.eva
        eva_installation_dir: path to eva module
    """
    config_file_path = eva_config_dir / EVA_CONFIG_FILE
    default_install_dir = eva_installation_dir
    dataset_location = EVA_DEFAULT_DIR / EVA_DATASET_DIR
    upload_dir = eva_config_dir / EVA_UPLOAD_DIR

    eva_config_dir.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # copy eva.yml into config path
    if not config_file_path.exists():
        default_config_path = get_base_config(default_install_dir).resolve()
        shutil.copy(str(default_config_path.resolve()), str(eva_config_dir.resolve()))

    # copy udfs to eva directory
    udfs_path = eva_config_dir / UDF_DIR
    if not udfs_path.exists():
        default_udfs_path = default_install_dir / UDF_DIR
        shutil.copytree(
            str(default_udfs_path.resolve()),
            str(udfs_path.resolve()),
        )

    # Update eva.yml with user specific paths
    with config_file_path.open("r+") as yml_file:
        config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)

        if config_obj is None:
            raise ValueError(f"Invalid yml file at {config_file_path}")

        mode = config_obj["core"]["mode"]

        config_obj["core"]["eva_installation_dir"] = str(default_install_dir.resolve())
        config_obj["core"]["datasets_dir"] = str(dataset_location.resolve())
        config_obj["core"]["catalog_database_uri"] = DB_DEFAULT_URI
        config_obj["storage"]["upload_dir"] = str(upload_dir.resolve())

        yml_file.seek(0)
        yml_file.write(yaml.dump(config_obj))
        yml_file.truncate()

    # set logger to appropriate level (debug or release)
    level = logging.WARN if mode == "release" else logging.DEBUG
    eva_logger.setLevel(level)
    eva_logger.debug(f"Setting logging level to: {str(level)}")
