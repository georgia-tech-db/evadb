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

from src.catalog.catalog_manager import CatalogManager
from src.server.command_handler import execute_query_fetch_all


class FiltersTest(unittest.TestCase):

    def setUp(self):
        CatalogManager().reset()
        load_query = """LOAD DATA INFILE 'data/m30.mp4' INTO MyVideo;"""
        execute_query_fetch_all(load_query)

    def test_object_filtering(self):
        create_udf_query = """CREATE UDF ObjectFilter
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (hasObj BOOLEAN)
                  TYPE  Filter
                  IMPL  'src/udfs/filters/object_filter.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT id FROM MyVideo WHERE ObjectFilter(data);"""
        execute_query_fetch_all(select_query)

    def test_color_filtering(self):
        create_udf_query = """CREATE UDF ColorFilter
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (hasRed BOOLEAN)
                  TYPE  Filter
                  IMPL  'src/udfs/filters/color_filter.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT id FROM MyVideo WHERE ColorFilter(data);"""
        execute_query_fetch_all(select_query)

    def test_cnn_filtering(self):
        create_udf_query = """CREATE UDF CNNFilter
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (hasCar BOOLEAN)
                  TYPE  Filter
                  IMPL  'src/udfs/filters/cnn_filter.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT id FROM MyVideo WHERE CNNFilter(data);"""
        execute_query_fetch_all(select_query)


if __name__ == "__main__":
    test = FiltersTest()
    test.setUp()
    test.test_object_filtering()
    test.test_color_filtering()
    test.test_cnn_filtering()
