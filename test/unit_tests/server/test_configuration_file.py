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
import os
import unittest
from test.markers import ray_skip_marker

from evadb.configuration.constants import EvaDB_CONFIG_FILE, EvaDB_ROOT_DIR


class ConfigurationFileTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @ray_skip_marker
    def test_check_configuration_file(self):
        config_file_path = os.path.join(EvaDB_ROOT_DIR, "evadb", EvaDB_CONFIG_FILE)
        import yaml

        with open(config_file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

            ray_setting = yaml_data.get("experimental").get("ray")
            self.assertEquals(ray_setting, False)
