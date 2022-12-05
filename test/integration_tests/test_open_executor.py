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

import numpy as np

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.server.command_handler import execute_query_fetch_all


class OpenExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ConfigurationManager()
        CatalogManager().reset()
        create_sample_image()

    @classmethod
    def tearDownClass(cls):
        file_remove("dummy.jpg")

    def test_open_simple_image(self):
        config = ConfigurationManager()
        upload_dir_from_config = config.get_value("storage", "upload_dir")
        img_path = os.path.join(upload_dir_from_config, "dummy.jpg")

        select_query = "OPEN '{}'".format(img_path)
        batch = execute_query_fetch_all(select_query)
        actual_img = batch.frames["data"].to_numpy()[0]

        expected_img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
        expected_img[0] -= 1
        expected_img[2] += 1

        self.assertEqual(actual_img.shape, expected_img.shape)
        self.assertEqual(np.sum(actual_img[0]), np.sum(expected_img[0]))
        self.assertEqual(np.sum(actual_img[1]), np.sum(expected_img[1]))
        self.assertEqual(np.sum(actual_img[2]), np.sum(expected_img[2]))
