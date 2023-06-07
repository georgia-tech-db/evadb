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
from test.util import (
    DummyObjectDetector,
    create_sample_video,
    load_udfs_for_testing,
    shutdown_ray,
    suffix_pytest_xdist_worker_id_to_dir,
)

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from evadb.binder.binder_utils import BinderError
from evadb.configuration.constants import EVA_DATABASE_DIR, EVA_ROOT_DIR
from evadb.executor.executor_utils import ExecutorError
from evadb.interfaces.relational.db import connect
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all


class TestLangchainLLM(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.db_dir = suffix_pytest_xdist_worker_id_to_dir(EVA_DATABASE_DIR)
        cls.conn = connect(cls.db_dir)
        cls.evadb = cls.conn._evadb

    def setUp(self):
        self.evadb.catalog().reset()
        load_udfs_for_testing(
            self.evadb,
        )

    def tearDown(self):
        shutdown_ray()

    def test_langchain_llm_gpt4all(self):
        conn = connect()
        cursor = conn.cursor()
        pdf_path1 = f"{EVA_ROOT_DIR}/data/documents/state_of_the_union.pdf"

        load_pdf = cursor.load(file_regex=pdf_path1, format="PDF", table_name="PDFss")
        load_pdf.execute()
        
        udf_check = cursor.drop_udf(
            "SentenceTransformerFeatureExtractor", if_exists=True
        ).execute()

        udf = cursor.create_udf(
            "SentenceTransformerFeatureExtractor",
            True,
            f"{EVA_ROOT_DIR}/evadb/udfs/sentence_transformer_feature_extractor.py",
        )
        udf.execute()

        udf_check = cursor.drop_udf(
            "GPT4AllQaUDF", if_exists=True
        ).execute()

        udf = cursor.create_udf(
            "GPT4AllQaUDF",
            True,
            f"{EVA_ROOT_DIR}/evadb/udfs/GPT4ALL.py",
        )
        udf.execute()

        pdf_table_similarity = (
                cursor.table("PDFss")
                .order(
                    """Similarity(
                        SentenceTransformerFeatureExtractor('When was the NATO created?'), SentenceTransformerFeatureExtractor(data)
                    )"""
                )
                .limit(3)
            )
        pdf_table_gpt = (
                pdf_table_similarity
                .cross_apply("GPT4AllQaUDF(data,'When was the NATO created?')", "objs(answers)")
            ).df()

        print(pdf_table_gpt)
        self.assertEqual(len(pdf_table_gpt), 3)
        self.assertTrue("pdfss.data" in pdf_table_gpt.columns)
        self.assertTrue("objs.answers" in pdf_table_gpt.columns)
