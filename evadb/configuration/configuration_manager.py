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
from pathlib import Path
from typing import Any

from evadb.configuration.bootstrap_environment import bootstrap_environment
from evadb.configuration.constants import EvaDB_DATABASE_DIR, EvaDB_INSTALLATION_DIR
from evadb.utils.logging_manager import logger


class ConfigurationManager(object):
    def __init__(self, evadb_dir: str = None) -> None:
        self._evadb_dir = evadb_dir or EvaDB_DATABASE_DIR
        self._config_obj = self._create_if_not_exists()

    def _create_if_not_exists(self):
        config_obj = bootstrap_environment(
            evadb_dir=Path(self._evadb_dir),
            evadb_installation_dir=Path(EvaDB_INSTALLATION_DIR),
        )
        return config_obj

    def _get(self, category: str, key: str) -> Any:
        """Retrieve a configuration value based on the category and key.

        Args:
            category (str): The category of the configuration.
            key (str): The key of the configuration within the category.

        Returns:
            Any: The retrieved configuration value.

        Raises:
            ValueError: If the YAML file is invalid or cannot be loaded.
        """
        config_obj = self._config_obj

        # Get value from the user-provided config file
        value = config_obj.get(category, {}).get(key)

        # cannot find the value, report invalid category, key combination
        if value is None:
            logger.exception(f"Invalid category and key combination {category}:{key}")

        return value

    def _update(self, category: str, key: str, value: str):
        config_obj = self._config_obj

        if category not in config_obj:
            config_obj[category] = {}

        config_obj[category][key] = value

    def get_value(self, category: str, key: str) -> Any:
        return self._get(category, key)

    def update_value(self, category, key, value) -> None:
        self._update(category, key, value)
