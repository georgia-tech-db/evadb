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

import pytest
import asyncio

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.interfaces.relational.db import connect

@pytest.mark.asyncio
class EVAAPITests(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
    
    # async def get_connection_async(self):
    #     reader, writer = await asyncio.open_connection(host="127.0.0.1", port=8803)
    #     return reader, writer

    def tearDown(self):
        # reader, writer = get_connection_async()
        connection = connect()
        cursor = connection.cursor()
        drop = cursor.query("DROP TABLE IF  EXISTS PDFss")
        drop.execute()

    def test_udf_eva_api(self):
        pdf_path = f"{EVA_ROOT_DIR}/data/documents/state_of_the_union.pdf"
        
        connection = connect()
        cursor = connection.cursor()

        load_pdf =cursor.load(file_regex=pdf_path,format="PDF",table_name="PDFss")
        load_pdf.execute()

        udf_check = cursor.query("DROP UDF IF  EXISTS SimilarityFeatureExtractor")
        udf_check.execute()
        udf = cursor.query(f"""CREATE UDF IF NOT EXISTS SimilarityFeatureExtractor
                            IMPL  '{EVA_ROOT_DIR}/eva/udfs/similarity_feature_extractor.py'""")
        udf.execute()

        table = cursor.table("PDFss")
        table_udf = table.cross_apply("SimilarityFeatureExtractor(data,'BLOOD')","objs(simiarity)")
        table_udf_data = table_udf.df()        
        self.assertEqual(len(table_udf_data.columns), 6)
        self.assertTrue("objs.simiarity" in table_udf_data.columns)
        self.assertTrue("pdfss.data" in table_udf_data.columns)
        self.assertTrue(
            all(
                isinstance(x, float) for x in table_udf_data["objs.simiarity"]
            )
        )

