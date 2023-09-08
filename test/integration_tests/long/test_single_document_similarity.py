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
import os
import unittest
from copy import deepcopy
from test.util import get_evadb_for_testing, load_functions_for_testing

import pytest

from evadb.server.command_handler import execute_query_fetch_all
from evadb.utils.generic_utils import try_to_import_fitz


@pytest.mark.notparallel
class SingleDocumentSimilarityTests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()

        load_functions_for_testing(self.evadb)

    def test_single_pdf_should_work(self):
        try_to_import_fitz()
        import fitz

        text_list = [
            "EvaDB is an AI-powered database",
            "I love playing switch when I am not doing research",
            "Playing basketball is a good exercise",
        ]

        # Create a PDF.
        doc = fitz.open()
        for text in text_list:
            doc.insert_page(
                -1,
                text=text,
                fontsize=11,
                width=595,
                height=842,
                fontname="Helvetica",
                color=(0, 0, 0),
            )
        doc.save("test.pdf")

        # Check PDF read.
        all_text = set(deepcopy(text_list))
        execute_query_fetch_all(
            self.evadb,
            "LOAD PDF 'test.pdf' INTO MyPDF",
        )
        res_batch = execute_query_fetch_all(self.evadb, "SELECT * FROM MyPDF")
        for i in range(len(res_batch)):
            all_text.remove(res_batch.frames["mypdf.data"][i])
        self.assertEqual(len(all_text), 0)

        # Create feature extrator.
        execute_query_fetch_all(
            self.evadb, "DROP FUNCTION IF EXISTS SentenceFeatureExtractor"
        )
        execute_query_fetch_all(
            self.evadb,
            "CREATE FUNCTION SentenceFeatureExtractor IMPL 'evadb/functions/sentence_feature_extractor.py'",
        )

        # Create index.
        execute_query_fetch_all(
            self.evadb,
            """
            CREATE INDEX qdrant_index
            ON MyPDF (SentenceFeatureExtractor(data))
            USING FAISS
        """,
        )

        # Ensure index scan is used.
        query = """
            SELECT data
            FROM MyPDF
            ORDER BY Similarity(SentenceFeatureExtractor('{}'), SentenceFeatureExtractor(data))
            LIMIT 1
        """
        res_batch = execute_query_fetch_all(self.evadb, f"EXPLAIN {query.format('xx')}")
        self.assertTrue("IndexScan" in res_batch.frames[0][0])

        # Search top match.
        all_text = set(deepcopy(text_list))
        for text in text_list:
            res_batch = execute_query_fetch_all(self.evadb, query.format(text))
            res_text = res_batch.frames["mypdf.data"][0]
            self.assertTrue(res_text in all_text)
            all_text.remove(res_text)

        # Remove PDF and table.
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyPDF")
        os.remove("test.pdf")
