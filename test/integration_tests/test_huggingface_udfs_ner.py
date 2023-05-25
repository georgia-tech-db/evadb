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
import unittest
from test.util import create_text_csv, file_remove

import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.executor.executor_utils import ExecutorError
from eva.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


class HuggingFaceNERTests(unittest.TestCase):
    """
    The tests below essentially check for the output format returned by HF.
    We need to ensure that it is in the format that we expect.
    """

    def setUp(self) -> None:
        CatalogManager().reset()

        query = """LOAD PDF 'data/documents/pdf_sample1.pdf' INTO MyPDFs;"""
        execute_query_fetch_all(query)


    def tearDown(self) -> None:
        execute_query_fetch_all("DROP TABLE IF EXISTS MyPDFs;")

    @pytest.mark.benchmark
    def test_named_entity_recognition_model(self):
        udf_name = "HFNERModel"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'ner'
        """
        execute_query_fetch_all(create_udf_query)

        select_query = f"SELECT data, {udf_name}(data) FROM MyPDFs;"
        output = execute_query_fetch_all(select_query)

        # Test that output has 7 columns
        self.assertEqual(len(output.frames.columns), 7)

        # Test that there exists a column with udf_name.entity
        self.assertTrue(udf_name.lower() + ".entity" in output.frames.columns)

        # Test that there exists a column with udf_name.score
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(drop_udf_query)
