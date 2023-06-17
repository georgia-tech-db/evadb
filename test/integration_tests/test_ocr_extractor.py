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
from test.util import (
    load_udfs_for_testing,
    shutdown_ray,
    suffix_pytest_xdist_worker_id_to_dir,
)

from evadb.configuration.constants import EvaDB_DATABASE_DIR, EvaDB_ROOT_DIR
from evadb.interfaces.relational.db import connect


class TestOCR(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
        cls.conn = connect(cls.db_dir)
        cls.evadb = cls.conn._evadb

    def setUp(self):
        self.evadb.catalog().reset()
        load_udfs_for_testing(
            self.evadb,
        )

    def tearDown(self):
        shutdown_ray()
        # todo: move these to relational apis as well

    def test_ocr_donut_huggingface(self):
        conn = connect()
        cursor = conn.cursor()
        img_path1 = f"{EvaDB_ROOT_DIR}/data/ocr/Example.jpg"
        cursor.drop_table(table_name="MyImage")
        load_pdf = cursor.load(
            file_regex=img_path1, format="IMAGE", table_name="MyImage"
        )
        load_pdf.execute()

        udf_check = cursor.query("DROP UDF IF  EXISTS OCRExtractor")
        udf_check.execute()
        udf = cursor.create_udf(
            "OCRExtractor",
            True,
            f"{EvaDB_ROOT_DIR}/evadb/udfs/ocr_extractor.py",
        )
        udf.execute()

        query = cursor.table("MyImage").cross_apply(
            "OCRExtractor(data)", "objs(ocr_data)"
        )
        output = query.df()
        print(output)
        self.assertEqual(len(output), 1)
        self.assertTrue("objs.ocr_data" in output.columns)
