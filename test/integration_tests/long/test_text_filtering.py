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
from test.util import suffix_pytest_xdist_worker_id_to_dir

import pytest

from evadb.configuration.constants import EvaDB_DATABASE_DIR, EvaDB_ROOT_DIR
from evadb.interfaces.relational.db import connect
from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class TextFilteringTests(unittest.TestCase):
    def setUp(self):
        self.db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
        self.conn = connect(self.db_dir)
        self.evadb = self.conn._evadb
        self.evadb.catalog().reset()

    def tearDown(self):
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyPDFs;")

    def test_text_filter(self):
        pdf_path = f"{EvaDB_ROOT_DIR}/data/documents/layout-parser-paper.pdf"
        cursor = self.conn.cursor()
        cursor.load(pdf_path, "MyPDFs", "pdf").df()
        load_pdf_data = cursor.table("MyPDFs").df()
        cursor.create_function(
            "TextFilterKeyword",
            True,
            f"{EvaDB_ROOT_DIR}/evadb/udfs/text_filter_keyword.py",
        ).df()
        filtered_data = (
            cursor.table("MyPDFs")
            .cross_apply("TextFilterKeyword(data, ['References'])", "objs(filtered)")
            .df()
        )
        filtered_data.dropna(inplace=True)
        import pandas as pd

        pd.set_option("display.max_colwidth", None)
        self.assertNotEqual(len(filtered_data), len(load_pdf_data))
