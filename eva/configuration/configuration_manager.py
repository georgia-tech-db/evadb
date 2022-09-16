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
from symbol import classdef
from typing import Any

import shutil
import yaml
from pathlib import Path
import importlib.resources

from eva.configuration.constants import EVA_CONFIG_FILE, EVA_DEFAULT_DIR, EVA_INSTALLATION_DIR, EVA_DATASET_DIR, EVA_UPLOAD_DIR, DB_DEFAULT_URI

class ConfigurationManager(object):
    yml_path = EVA_DEFAULT_DIR / EVA_CONFIG_FILE

    def __init__(self) -> None:
        raise ValueError("ConfigurationManager should not be initialized. Instead call methods directly.")

    @classmethod
    def reload(cls) -> None:
        shutil.rmtree(EVA_DEFAULT_DIR)
        cls._create_if_not_exists()

    @staticmethod
    def _get_base_config() -> Path:
        """
        Get path to eva.yml source path.
        This file will be copied to user's .eva/ directory.
        """
        # if eva package is installed into environment
        if importlib.resources.is_resource("eva", EVA_CONFIG_FILE):
            with importlib.resources.path("eva", EVA_CONFIG_FILE) as yml_path:
                return yml_path
        else:
            # For local dev environments without package installed
            return EVA_INSTALLATION_DIR / EVA_CONFIG_FILE

    @classmethod
    def _create_if_not_exists(cls) -> None:
        if EVA_DEFAULT_DIR.exists():
            return
    
        # Create user .eva/ directory and copy over eva.yml
        EVA_DEFAULT_DIR.mkdir(parents=True, exist_ok=True)
        if not cls.yml_path.exists():
            eva_source_path = cls._get_base_config()
            shutil.copy(str(eva_source_path.resolve()), str(EVA_DEFAULT_DIR.resolve()))
        
        # copy udfs to eva directory
        udfs_path = EVA_DEFAULT_DIR / "udfs"
        if not udfs_path.exists():
            default_udfs_path = EVA_INSTALLATION_DIR / "udfs"
            shutil.copytree(str(default_udfs_path.resolve()), str(udfs_path.resolve()))
        
        EVA_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        cls._update_value("core", "datasets_dir", str(EVA_DATASET_DIR.resolve()))
        cls._update_value("core", "catalog_database_uri", DB_DEFAULT_URI)
        cls._update_value("storage", "upload_dir", str(EVA_UPLOAD_DIR.resolve()))

    @classmethod
    def _read_config_from_file(cls) -> Any:
        with cls.yml_path.open("r") as yml_file:
            return yaml.safe_load(yml_file)

    @classmethod
    def _get_value(cls, category, key):
        return cls._read_config_from_file()[category][key]
    
    @classmethod
    def get_value(cls, category, key):
        cls._create_if_not_exists()
        return cls._get_value(category, key)

    @classmethod
    def _update_value(cls, category, key, value):
        cfg = cls._read_config_from_file()
        cfg[category][key] = value
        with cls.yml_path.open("w") as yml_file:
            yaml.dump(cfg, yml_file)
    
    @classmethod
    def update_value(cls, category, key, value):
        cls._create_if_not_exists()
        return cls._update_value(category, key, value)
