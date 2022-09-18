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
from typing import Any

import yaml

from eva.configuration.bootstrap_environment import bootstrap_environment
from eva.configuration.config_utils import read_value_config, update_value_config
from eva.configuration.constants import (
    EVA_CONFIG_FILE,
    EVA_DEFAULT_DIR,
    EVA_INSTALLATION_DIR,
)


class ConfigurationManager(object):
    _instance = None
    _yml_path = EVA_DEFAULT_DIR / EVA_CONFIG_FILE

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)

            bootstrap_environment(
                eva_config_dir=EVA_DEFAULT_DIR,
                eva_installation_dir=EVA_INSTALLATION_DIR,
            )  # Setup eva in home directory

        return cls._instance

    @classmethod
    def _get(cls, category: str, key: str) -> Any:
        with cls._yml_path.open("r") as yml_file:
            config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)
            if config_obj is None:
                raise ValueError(f"Invalid yml file at {cls._yml_path}")
            return config_obj[category][key]

    @classmethod
    def _update(cls, category: str, key: str, value: str):
        # read config file
        with cls._yml_path.open("r") as yml_file:
            config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)
            if config_obj is None:
                raise ValueError(f"Invalid yml file at {cls._yml_path}")

        # update value and write back to config file
        config_obj[category][key] = value
        with cls._yml_path.open("w") as yml_file:
            yml_file.write(yaml.dump(config_obj))

    def get_value(self, category: str, key: str) -> Any:
        return self._get(category, key)

    def update_value(self, category, key, value) -> None:
        self._update(category, key, value)
