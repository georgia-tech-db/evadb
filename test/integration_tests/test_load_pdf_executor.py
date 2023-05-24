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
from test.util import (
    shutdown_ray,
)

import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all
from langchain.document_loaders import PyPDFLoader


@pytest.mark.notparallel
class LoadExecutorTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()

    def tearDown(self):
        shutdown_ray()

        execute_query_fetch_all("DROP TABLE IF EXISTS pdfs;")

    def test_load_pdfs(self):
        pdf_path = f"{EVA_ROOT_DIR}/data/documents/pdf_sample1.pdf"
        loader = PyPDFLoader(pdf_path)
        num_pages = len(loader.load())
        execute_query_fetch_all(
            f"""LOAD PDF '{pdf_path}' INTO pdfs;"""
        )
        result = execute_query_fetch_all("SELECT * from pdfs;")
        self.assertEqual(len(result.columns), 4)
        self.assertEqual(len(result), num_pages)


if __name__ == "__main__":
    unittest.main()
