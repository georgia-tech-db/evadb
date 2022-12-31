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
import importlib
import os
import shutil
import unittest


class EVAImportTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_eva_cli_imports(self):
        """
        Testing imports for running client and server packages,
        when current working directory is changed.
        """
        cur_dir = os.getcwd()
        new_dir = os.path.join("test_eva", "test")
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        os.chdir(new_dir)
        _ = importlib.import_module("eva.eva_cmd_client")
        _ = importlib.import_module("eva.eva_server")
        os.chdir(cur_dir)
        shutil.rmtree(new_dir)
