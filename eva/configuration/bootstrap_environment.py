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

from pathlib import Path
import importlib.resources as importlib_resources
import os
import shutil
import yaml

from eva.configuration.dictionary import EVA_INSTALLATION_DIR, \
    EVA_DEFAULT_DIR, EVA_DATASET_DIR, DB_DEFAULT_URI, \
    EVA_CONFIG_FILE, EVA_UPLOAD_DIR
from eva.configuration.config_utils import read_value_config, \
    update_value_config


def get_base_config():
    ymlpath = None
    if importlib_resources.is_resource('eva', EVA_CONFIG_FILE):
        with importlib_resources.path('eva', EVA_CONFIG_FILE)as path:
            ymlpath = path
    else:  # For local dev environments without package installed
        ymlpath = os.path.join(EVA_INSTALLATION_DIR, EVA_CONFIG_FILE)
    return ymlpath


def bootstrap_environment():
    # create eva directory in user home
    eva_home_directory = Path(EVA_DEFAULT_DIR)
    eva_home_directory.mkdir(parents=True, exist_ok=True)

    # copy default config to eva directory
    config_path = eva_home_directory / EVA_CONFIG_FILE
    if not config_path.exists():
        default_config_path = get_base_config()
        shutil.copy(str(default_config_path), str(config_path))

    # copy udfs to eva directory
    udfs_path = Path(EVA_DEFAULT_DIR + "/udfs/")
    if not udfs_path.exists():
        default_udfs_path = EVA_INSTALLATION_DIR + "/udfs/"
        shutil.copytree(default_udfs_path, str(udfs_path))

    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # fill default values for dataset and database if not present
    dataset_location = read_value_config(cfg, "core", "datasets_dir")
    database_uri = read_value_config(cfg, "core", "catalog_database_uri")
    upload_location = read_value_config(cfg, "storage", "upload_dir")

    if not dataset_location or \
       not database_uri or \
       not upload_location:
        if not dataset_location:
            dataset_location = str(
                eva_home_directory / EVA_DATASET_DIR)
            update_value_config(cfg, "core", "datasets_dir",
                                dataset_location)
        if not database_uri:
            database_uri = DB_DEFAULT_URI
            update_value_config(cfg, "core", "catalog_database_uri",
                                database_uri)

        if not upload_location:
            upload_location = str(
                eva_home_directory / EVA_UPLOAD_DIR)
            update_value_config(cfg, "storage", "upload_dir",
                                upload_location)
        # update config on disk
        with open(config_path, 'w') as ymlfile:
            ymlfile.write(yaml.dump(cfg))
