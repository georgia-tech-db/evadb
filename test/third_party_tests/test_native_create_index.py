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
from pathlib import Path
from test.markers import macos_skip_marker
from test.util import get_evadb_for_testing, load_functions_for_testing

import numpy as np
import pandas as pd
import pytest

from evadb.catalog.catalog_type import VectorStoreType
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.storage.storage_engine import StorageEngine
from evadb.utils.generic_utils import try_to_import_faiss


@pytest.mark.notparallel
class CreateIndexTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()

    def test_native_engine_should_create_index(self):
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
        execute_query_fetch_all(self.evadb, query)

        # Create table.
        query = """USE test_data_source {
            CREATE TABLE test_vector (embedding vector(3))
        }"""
        execute_query_fetch_all(self.evadb, query)

        # Insert data.
        vector_list = [
            [0,0,0],
            [1,1,1],
            [2,2,2],
        ]
        for vector in vector_list:
            query = f"""USE test_data_source {{
                INSERT INTO test_vector (embedding) VALUES ('{vector}')
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

        # Clean up.
        query = "USE test_data_source { DROP INDEX test_index }"
        execute_query_fetch_all(self.evadb, query)
        query = "USE test_data_source { DROP TABLE test_vector }"
        execute_query_fetch_all(self.evadb, query)
