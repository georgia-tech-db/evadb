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
import tempfile
import unittest
from pathlib import Path

import pytest

from eva.configuration.bootstrap_environment import bootstrap_environment
from eva.configuration.constants import EVA_CONFIG_FILE, EVA_INSTALLATION_DIR, UDF_DIR


class BootstrapEnvironmentTests(unittest.TestCase):
    def test_bootstrap_environment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            bootstrap_environment(temp_dir_path, EVA_INSTALLATION_DIR)

            config_path = temp_dir_path / EVA_CONFIG_FILE
            assert config_path.exists()

            udfs_dir = temp_dir_path / UDF_DIR
            assert udfs_dir.exists()

    def test_invalid_eva_path_setup(self):
        with pytest.raises(OSError):
            with tempfile.TemporaryDirectory() as temp_dir:
                bootstrap_environment(Path(temp_dir), Path("invalid", "dir"))
