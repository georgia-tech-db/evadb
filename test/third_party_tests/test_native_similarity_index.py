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
    create_sample_image,
    get_evadb_for_testing,
    load_functions_for_testing,
)

import pytest

from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class CreateIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()

        # Get sample image.
        cls.img_path = create_sample_image()

        # Load functions.
        load_functions_for_testing(cls.evadb, mode="debug")

        # Create database.
        params = {
            "user": "eva",
            "password": "password",
            "host": "localhost",
            "port": "5432",
            "database": "evadb",
        }
        query = f"""CREATE DATABASE test_data_source
                    WITH ENGINE = "postgres",
                    PARAMETERS = {params};"""
        execute_query_fetch_all(cls.evadb, query)

    @classmethod
    def tearDownClass(cls):
        # Clean up.
        query = "USE test_data_source { DROP INDEX test_index }"
        execute_query_fetch_all(cls.evadb, query)
        query = "USE test_data_source { DROP TABLE test_vector }"
        execute_query_fetch_all(cls.evadb, query)

    def test_native_engine_should_create_index(self):
        # Create table.
        query = """USE test_data_source {
            CREATE TABLE test_vector (idx INTEGER, dummy INTEGER, embedding vector(27))
        }"""
        execute_query_fetch_all(self.evadb, query)

        # Insert data.
        vector_list = [
            [0.0 for _ in range(9)] + [1.0 for _ in range(9)] + [2.0 for _ in range(9)],
            [1.0 for _ in range(9)] + [2.0 for _ in range(9)] + [3.0 for _ in range(9)],
            [2.0 for _ in range(9)] + [3.0 for _ in range(9)] + [4.0 for _ in range(9)],
            [3.0 for _ in range(9)] + [4.0 for _ in range(9)] + [5.0 for _ in range(9)],
            [4.0 for _ in range(9)] + [5.0 for _ in range(9)] + [6.0 for _ in range(9)],
        ]
        for idx, vector in enumerate(vector_list):
            query = f"""USE test_data_source {{
                INSERT INTO test_vector (idx, dummy, embedding) VALUES ({idx}, {idx}, '{vector}')
            }}"""
            execute_query_fetch_all(self.evadb, query)

        # Create index.
        query = """CREATE INDEX test_index
            ON test_data_source.test_vector (embedding)
            USING PGVECTOR"""
        execute_query_fetch_all(self.evadb, query)

        # Check the existence of index.
        query = """USE test_data_source {
            SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'test_vector'
        }"""
        df = execute_query_fetch_all(self.evadb, query).frames

        self.assertEqual(len(df), 1)
        self.assertEqual(df["indexname"][0], "test_index")
        self.assertEqual(
            df["indexdef"][0],
            """CREATE INDEX test_index ON public.test_vector USING hnsw (embedding vector_l2_ops)""",
        )

        # Check the index scan plan.
        query = f"""SELECT idx, embedding FROM test_data_source.test_vector
            ORDER BY Similarity(DummyFeatureExtractor(Open('{self.img_path}')), embedding)
            LIMIT 1"""
        df = execute_query_fetch_all(self.evadb, f"EXPLAIN {query}").frames
        self.assertIn("VectorIndexScan", df[0][0])

        # Check results.
        df = execute_query_fetch_all(self.evadb, query).frames
        self.assertEqual(df["test_vector.idx"][0], 0)
        self.assertNotIn("test_vector.dummy", df.columns)
