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
            cls._create_if_not_exists()

        return cls._instance

    @classmethod
    def _create_if_not_exists(cls):
        if not cls._yml_path.exists():
            bootstrap_environment(
                eva_config_dir=EVA_DEFAULT_DIR,
                eva_installation_dir=EVA_INSTALLATION_DIR,
            )

    @classmethod
    def _get(cls, category: str, key: str) -> Any:
        with cls._yml_path.open("r") as yml_file:
            config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)
            if config_obj is None:
                raise ValueError(f"Invalid yaml file at {cls._yml_path}")
            key_error = (
                f"Add the entry '{category}: {key}' to the yaml file. Or, if "
                f"you did not modify the yaml file, remove it (rm {cls._yml_path}),"
                f"and the system will auto-generate one."
            )
            if category not in config_obj:
                raise KeyError(
                    f"Missing category '{category}' in the yaml file at {cls._yml_path}. {key_error}"
                )
            if key not in config_obj[category]:
                raise KeyError(
                    f"Missing key {key} for the category {category} in the yaml file at {cls._yml_path}. {key_error}"
                )
            return config_obj[category][key]

    @classmethod
    def _update(cls, category: str, key: str, value: str):
        with cls._yml_path.open("r+") as yml_file:
            config_obj = yaml.load(yml_file, Loader=yaml.FullLoader)

            if config_obj is None:
                raise ValueError(f"Invalid yml file at {cls._yml_path}")

            key_error = (
                f"Cannot update the key {key} for the missing category {category}."
                f"Add the entry '{category}' to the yaml file. Or, if "
                f"you did not modify the yaml file, remove it (rm {cls._yml_path}),"
                f"and the system will auto-generate one."
            )
            if category not in config_obj:
                raise KeyError(
                    f"Missing category '{category}' in the yaml file at {cls._yml_path}. {key_error}"
                )
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
