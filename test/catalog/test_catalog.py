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
import unittest
import logging

from src.catalog.catalog_manager import CatalogManager
from src.spark.session import Session


def suppress_py4j_logging():
    logger = logging.getLogger('py4j')
    logger.setLevel(logging.ERROR)


class CatalogManagerTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        suppress_py4j_logging()

    def tearDown(self):
        self.session = Session()
        self.session.stop()

    def test_catalog_manager_singleton_pattern(self):
        x = CatalogManager()
        y = CatalogManager()
        self.assertEqual(x, y)


if __name__ == '__main__':

    unittest.main()
