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
import os
from pathlib import Path
from typing import Any

import yaml

from eva.configuration.bootstrap_environment import (
    bootstrap_environment,
    create_directories_and_get_default_config_values,
)
from eva.utils.logging_manager import logger
from eva.configuration.constants import (
    EVA_CONFIG_FILE,
    EVA_DATABASE_DIR,
    EVA_INSTALLATION_DIR,
)


class ConfigurationManager(object):
    _yml_path = None

    def __new__(cls, *args, **kwargs):
        eva_db_dir = kwargs.get("EVA_DATABASE_DIR", EVA_DATABASE_DIR)
        if not hasattr(cls, "_instance"):
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._eva_db_dir = eva_db_dir
            cls._yml_path = Path(eva_db_dir) / EVA_CONFIG_FILE
            cls._create_if_not_exists()

            default_yml_file = Path(EVA_INSTALLATION_DIR) / "eva.yml"
            with default_yml_file.open("r") as yml_file:
                cls._default_config_obj = yaml.load(yml_file, yaml.FullLoader)

        return cls._instance

    @classmethod
    def suffix_pytest_xdist_worker_id_to_dir(cls, path: str):
        try:
            worker_id = os.environ["PYTEST_XDIST_WORKER"]
            path = Path(str(worker_id) + "_" + path)
        except KeyError:
            pass
        return path

    @classmethod
    def _create_if_not_exists(cls):
        # if not cls._yml_path.exists():
        initial_eva_db_dir = cls._eva_db_dir

        # parallelize tests using pytest-xdist
        # activated only under pytest-xdist
        # Changes db dir From EVA_DB_DIR To gw1_EVA_DB_DIR
        # (where gw1 is worker id)
        updated_eva_config_dir = cls.suffix_pytest_xdist_worker_id_to_dir(
            initial_eva_db_dir
        )
        cls._eva_db_dir = updated_eva_config_dir
        cls._yml_path = Path(updated_eva_config_dir) / EVA_CONFIG_FILE
        bootstrap_environment(
            eva_db_dir=Path(updated_eva_config_dir),
            eva_installation_dir=EVA_INSTALLATION_DIR,
        )

    @classmethod
    def _get(cls, category: str, key: str) -> Any:
        """Retrieve a configuration value based on the category and key.

        Args:
            category (str): The category of the configuration.
            key (str): The key of the configuration within the category.

        Returns:
            Any: The retrieved configuration value.

        Raises:
            ValueError: If the YAML file is invalid or cannot be loaded.
        """
        config_obj = {}
        with cls._yml_path.open("r") as yml_file:
            config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)
        if config_obj is None:
            raise ValueError(f"Invalid YAML file at {cls._yml_path}")

        # Get value from the user-provided config file
        value = config_obj.get(category, {}).get(key)

        # Try default config values
        if value is None:
            value = create_directories_and_get_default_config_values(
                Path(cls._eva_db_dir), Path(EVA_INSTALLATION_DIR), category, key
            )

        # Try config value in the system default config YAML file
        if value is None:
            value = cls._default_config_obj.get(category, {}).get(key)

        # cannot find the value, report invalid category, key combination
        if value is None:
            logger.exception(f"Invalid category and key combination {category}:{key}")

        return value

    @classmethod
    def _update(cls, category: str, key: str, value: str):
        with cls._yml_path.open("r+") as yml_file:
            config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)

            if config_obj is None:
                raise ValueError(f"Invalid yml file at {cls._yml_path}")

            if category not in config_obj:
                config_obj[category] = {}

            config_obj[category][key] = value
            yml_file.seek(0)
            yml_file.write(yaml.dump(config_obj))
            yml_file.truncate()

    @classmethod
    def get_value(cls, category: str, key: str) -> Any:
        return cls._get(category, key)

    @classmethod
    def update_value(cls, category, key, value) -> None:
        cls._update(category, key, value)
