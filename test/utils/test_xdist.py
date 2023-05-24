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

from eva.configuration.configuration_manager import ConfigurationManager


class XdistTests(unittest.TestCase):

    def test_suffix_pytest_xdist_worker_id_to_dir(self):
        os.environ["PYTEST_XDIST_WORKER"] = "gw1"
        foo_path = "foo"
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
