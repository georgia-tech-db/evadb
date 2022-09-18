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

    def get_value(self, category, key):
        return read_value_config(self._yml_path, category, key)

    def update_value(self, category, key, value):
        update_value_config(self._yml_file, category, key, value)
