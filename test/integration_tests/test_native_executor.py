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
from test.util import get_evadb_for_testing, shutdown_ray

import pytest

from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class NativeExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

    def tearDown(self):
        shutdown_ray()

    @pytest.mark.skip(reason="Does not work under the current setup")
    def test_should_run_simple_query_in_sqlalchemy(self):
        # Create database.
        params = {
            "user": "eva",
            "password": "password",
            "host": "127.0.0.1",
            "port": "5432",
            "database": "test",
        }
        query = """CREATE DATABASE postgres_data
                    WITH ENGINE = "postgres",
                    PARAMETERS = {};""".format(
            params
        )
        execute_query_fetch_all(self.evadb, query)

        # Create table.
        execute_query_fetch_all(
            self.evadb,
            """USE postgres_data {
                CREATE TABLE test_table (
                    name VARCHAR(10),
                    age INT,
                    comment VARCHAR(100)
                )
            };""",
        )
        execute_query_fetch_all(
            self.evadb,
            """USE postgres_data {
                INSERT INTO test_table (
                    name, age, comment
                ) VALUES (
                    'aa', 1, 'aaaa'
                )
            }
            """,
        )

        # Select.
        res_batch = execute_query_fetch_all(
            self.evadb,
            """USE postgres_data {
                SELECT * FROM test_table
            }
            """,
        )
        self.assertEqual(len(res_batch), 1)
        self.assertEqual(res_batch.frames["name"][0], "aa")
        self.assertEqual(res_batch.frames["age"][0], 1)
        self.assertEqual(res_batch.frames["comment"][0], "aaaa")

        # DROP table.
        execute_query_fetch_all(
            self.evadb,
            """USE postgres_data {
                DROP TABLE test_table
            }
            """,
        )
