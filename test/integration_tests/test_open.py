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

from test.util import create_sample_image, file_remove
from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.udf_bootstrap_queries import init_builtin_udfs


class OpenTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        ConfigurationManager()

        init_builtin_udfs()

        # Insert image path.
        create_sample_image()
        create_table_query = """CREATE TABLE IF NOT EXISTS testOpenTable (num1 INTEGER, num2 INTEGER);"""
        execute_query_fetch_all(create_table_query)

    def tearDown(self):
        file_remove("dummy.jpg")

    def test_open_should_open_image(self):
        # Test query runs successfully with Open function call.
        config = ConfigurationManager()
        upload_dir_from_config = config.get_value("storage", "upload_dir")
        img_path = os.path.join(upload_dir_from_config, "dummy.jpg")
        select_query = """SELECT * FROM testOpenTable WHERE Open("{}");""".format(img_path)
        execute_query_fetch_all(select_query)
