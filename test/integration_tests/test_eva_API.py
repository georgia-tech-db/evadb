# coding=utf-8
# Copyright 2018-2023 EVA
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

from eva.configuration.constants import EVA_ROOT_DIR
from eva.interfaces.relational.db import connect

@pytest.mark.asyncio
class EVAAPITests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

    def test_udf_eva_api(self):
        pdf_path = f"{EVA_ROOT_DIR}/data/documents/state_of_the_union.pdf"

        conn = connect()

        load_pdf = conn.load(file_regex=pdf_path, format="PDF", table_name="PDFss")
        load_pdf.execute()

        udf_check = conn.query("DROP UDF IF  EXISTS SimilarityFeatureExtractor")
        udf_check.execute()

        udf = conn.query(
            f"""CREATE UDF IF NOT EXISTS SimilarityFeatureExtractor
                            IMPL  '{EVA_ROOT_DIR}/eva/udfs/similarity_feature_extractor.py'"""
        )
        udf.execute()

        conn.create_vector_index(
            "faiss_index",
            table_name="PDFss",
            expr="SimilarityFeatureExtractor(data)",
            using="QDRANT",
        ).df()

        rel = (
            conn.table("PDFss")
            .order(
                "Similarity(SimilarityFeatureExtractor('When was the NATO created?'), SimilarityFeatureExtractor(data))"
            )
            .limit(1)
            .select("data")
        ).df()
        self.assertEqual(len(rel), 1)
        self.assertTrue("pdfss.data" in rel.columns)
