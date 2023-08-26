# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from test.util import get_evadb_for_testing

import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class LoadPDFExecutorTests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

    def tearDown(self):
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyPDFs;")

    def test_load_pdfs(self):
        pdf_path = f"{EvaDB_ROOT_DIR}/data/documents/pdf_sample1.pdf"

        import fitz

        doc = fitz.open(pdf_path)
        number_of_paragraphs = 0
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b["type"] == 0:
                    block_string = ""
                    for lines in b["lines"]:
                        for span in lines["spans"]:
                            if span["text"].strip():
                                block_string += span["text"]
                    number_of_paragraphs += 1

        execute_query_fetch_all(self.evadb, f"""LOAD PDF '{pdf_path}' INTO MyPDFs;""")
        result = execute_query_fetch_all(self.evadb, "SELECT * from MyPDFs;")
        self.assertEqual(len(result.columns), 5)
        self.assertEqual(len(result), number_of_paragraphs)
