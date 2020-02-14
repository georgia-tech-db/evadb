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

import yaml
from src.configuration.dictionary import EVA_DIR
import os

class ConfigurationManager(object):

    _instance = None
    _cfg = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)

            with open(os.path.join(EVA_DIR, "eva.yml"), 'r') as ymlfile:
                cls._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

        return cls._instance

    def get_value(self, category, key):
        # get category information
        category_data = self._cfg.get(category, None)

        # get key information
        value = None
        if category_data is not None:
            value = category_data.get(key, None)
            return value