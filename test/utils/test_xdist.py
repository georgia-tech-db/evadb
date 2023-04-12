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
import unittest
from pathlib import Path

from eva.catalog.sql_config import SQLConfig
from eva.configuration.configuration_manager import ConfigurationManager
from eva.utils.generic_utils import prefix_worker_id_to_path


class XdistTests(unittest.TestCase):
    def test_prefix_worker_id_to_uri_in_sql_config(self):
        os.environ["PYTEST_XDIST_WORKER"] = "gw1"
        sql_config = SQLConfig()
        self.assertTrue("gw1" in sql_config.worker_uri)

        os.environ["PYTEST_XDIST_WORKER"] = ""
        sql_config = SQLConfig()
        self.assertFalse("gw1" in sql_config.worker_uri)

    def test_suffix_pytest_xdist_worker_id_to_dir(self):
        os.environ["PYTEST_XDIST_WORKER"] = "gw1"
        foo_path = Path("foo")
        configuration_manager = ConfigurationManager()
        updated_path = configuration_manager.suffix_pytest_xdist_worker_id_to_dir(
            foo_path
        )
        self.assertTrue("gw1" in str(updated_path))

        os.environ["PYTEST_XDIST_WORKER"] = ""
        updated_path = configuration_manager.suffix_pytest_xdist_worker_id_to_dir(
            foo_path
        )
        self.assertFalse("gw1" in str(updated_path))

    def test_prefix_worker_id_to_path_in_generic_utils(self):
        os.environ["PYTEST_XDIST_WORKER"] = "gw1"
        foo_path = Path("foo")
        updated_path = prefix_worker_id_to_path(foo_path)
        self.assertTrue("gw1" in str(updated_path))

        os.environ["PYTEST_XDIST_WORKER"] = ""
        updated_path = prefix_worker_id_to_path(foo_path)
        self.assertFalse("gw1" in str(updated_path))
