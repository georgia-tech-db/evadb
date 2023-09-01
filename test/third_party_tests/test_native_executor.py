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

from evadb.executor.executor_utils import ExecutorError
from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class NativeExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

    def tearDown(self):
        shutdown_ray()
        self._drop_table_in_native_database()

    def _create_table_in_native_database(self):
        execute_query_fetch_all(
            self.evadb,
            """USE test_data_source {
                CREATE TABLE test_table (
                    name VARCHAR(10),
                    age INT,
                    comment VARCHAR (100)
                )
            }""",
        )

    def _insert_value_into_native_database(self, col1, col2, col3):
        execute_query_fetch_all(
            self.evadb,
            f"""USE test_data_source {{
                INSERT INTO test_table (
                    name, age, comment
                ) VALUES (
                    '{col1}', {col2}, '{col3}'
                )
            }}""",
        )

    def _drop_table_in_native_database(self):
        execute_query_fetch_all(
            self.evadb,
            """USE test_data_source {
                DROP TABLE IF EXISTS test_table
            }""",
        )

    def _create_evadb_table_using_select_query(self):
        execute_query_fetch_all(
            self.evadb,
            """CREATE TABLE eva_table AS SELECT name, age FROM test_data_source.test_table;""",
        )

        # check if the create table is successful
        res_batch = execute_query_fetch_all(self.evadb, "Select * from eva_table")
        self.assertEqual(len(res_batch), 2)
        self.assertEqual(res_batch.frames["eva_table.name"][0], "aa")
        self.assertEqual(res_batch.frames["eva_table.age"][0], 1)
        self.assertEqual(res_batch.frames["eva_table.name"][1], "bb")
        self.assertEqual(res_batch.frames["eva_table.age"][1], 2)

        execute_query_fetch_all(
            self.evadb,
            "DROP TABLE IF EXISTS eva_table;",
        )

    def _execute_evadb_query(self):
        self._create_table_in_native_database()
        self._insert_value_into_native_database("aa", 1, "aaaa")
        self._insert_value_into_native_database("bb", 2, "bbbb")

        res_batch = execute_query_fetch_all(
            self.evadb,
            "SELECT * FROM test_data_source.test_table",
        )
        self.assertEqual(len(res_batch), 2)
        self.assertEqual(res_batch.frames["test_table.name"][0], "aa")
        self.assertEqual(res_batch.frames["test_table.age"][0], 1)
        self.assertEqual(res_batch.frames["test_table.name"][1], "bb")
        self.assertEqual(res_batch.frames["test_table.age"][1], 2)

        self._create_evadb_table_using_select_query()
        self._drop_table_in_native_database()

    def _execute_native_query(self):
        self._create_table_in_native_database()
        self._insert_value_into_native_database("aa", 1, "aaaa")

        res_batch = execute_query_fetch_all(
            self.evadb,
            """USE test_data_source {
                SELECT * FROM test_table
            }""",
        )
        self.assertEqual(len(res_batch), 1)

        self.assertEqual(res_batch.frames["name"][0], "aa")
        self.assertEqual(res_batch.frames["age"][0], 1)
        self.assertEqual(res_batch.frames["comment"][0], "aaaa")

        self._drop_table_in_native_database()

    def _raise_error_on_multiple_creation(self):
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
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(self.evadb, query)

    def _raise_error_on_invalid_connection(self):
        params = {
            "user": "xxxxxx",
            "password": "xxxxxx",
            "host": "localhost",
            "port": "5432",
            "database": "evadb",
        }
        query = f"""CREATE DATABASE invaid
                    WITH ENGINE = "postgres",
                    PARAMETERS = {params};"""
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(self.evadb, query)

    def test_should_run_query_in_postgres(self):
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

        # Test executions.
        self._execute_native_query()
        self._execute_evadb_query()

        # Test error.
        self._raise_error_on_multiple_creation()
        self._raise_error_on_invalid_connection()

    def test_should_run_query_in_sqlite(self):
        # Create database.
        params = {
            "database": "evadb.db",
        }
        query = f"""CREATE DATABASE test_data_source
                    WITH ENGINE = "sqlite",
                    PARAMETERS = {params};"""
        execute_query_fetch_all(self.evadb, query)

        # Test executions.
        self._execute_native_query()
        self._execute_evadb_query()

    def test_should_run_query_in_mysql(self):
        # Create database.
        params = {
            "user": "eva",
            "password": "password",
            "host": "localhost",
            "port": "3306",
            "database": "evadb",
        }
        query = f"""CREATE DATABASE test_data_source
                    WITH ENGINE = "mysql",
                    PARAMETERS = {params};"""
        execute_query_fetch_all(self.evadb, query)

        # Test executions.
        self._execute_native_query()
        self._execute_evadb_query()


if __name__ == "__main__":
    unittest.main()
