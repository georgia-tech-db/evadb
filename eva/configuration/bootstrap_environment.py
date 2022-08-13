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
import shutil
from logging import DEBUG, WARN
from pathlib import Path

import yaml

from eva.configuration.config_utils import read_value_config, update_value_config
from eva.configuration.dictionary import (
    DB_DEFAULT_URI,
    EVA_CONFIG_FILE,
    EVA_DATASET_DIR,
    EVA_DEFAULT_DIR,
    EVA_INSTALLATION_DIR,
    EVA_UPLOAD_DIR,
)
from eva.utils.logging_manager import logger


def get_base_config() -> Path:
    if importlib_resources.is_resource("eva", EVA_CONFIG_FILE):
        with importlib_resources.path("eva", EVA_CONFIG_FILE) as yml_path:
            return yml_path
    else:
        # For local dev environments without package installed
        return EVA_INSTALLATION_DIR / EVA_CONFIG_FILE


def bootstrap_environment():
    # create eva directory in user home
    EVA_DEFAULT_DIR.mkdir(parents=True, exist_ok=True)

    # copy default config to eva directory
    config_path = EVA_DEFAULT_DIR / EVA_CONFIG_FILE
    if not config_path.exists():
        default_config_path = get_base_config().resolve()
        shutil.copy(
            str(default_config_path.resolve()), str(config_path.parent.resolve())
        )

    # copy udfs to eva directory
    udfs_path = EVA_DEFAULT_DIR / "udfs"
    if not udfs_path.exists():
        default_udfs_path = EVA_INSTALLATION_DIR / "udfs"
        shutil.copytree(str(default_udfs_path.resolve()), str(udfs_path.resolve()))

    with config_path.open("r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # set logging level
    mode = read_value_config(cfg, "core", "mode")
    assert mode == "debug" or mode == "release"
    level = None
    if mode == "debug":
        level = DEBUG
    else:
        level = WARN

    logger.setLevel(level)
    logger.debug("Setting logging level to: " + str(level))

    # fill default values for dataset, database and upload loc if not present
    dataset_location = read_value_config(cfg, "core", "datasets_dir")
    database_uri = read_value_config(cfg, "core", "catalog_database_uri")
    upload_location = None

    if not dataset_location or not database_uri or not upload_location:
        if not dataset_location:
            dataset_location = EVA_DEFAULT_DIR / EVA_DATASET_DIR
            update_value_config(
                cfg, "core", "datasets_dir", str(dataset_location.resolve())
            )
        if not database_uri:
            database_uri = DB_DEFAULT_URI
            update_value_config(cfg, "core", "catalog_database_uri", database_uri)

        upload_location = EVA_DEFAULT_DIR / EVA_UPLOAD_DIR
        update_value_config(
            cfg, "storage", "upload_dir", str(upload_location.resolve())
        )

        # Create upload directory in eva home directory if it does not exist
        upload_location.mkdir(parents=True, exist_ok=True)

        # update config on disk
        with config_path.open("w") as ymlfile:
            ymlfile.write(yaml.dump(cfg))
