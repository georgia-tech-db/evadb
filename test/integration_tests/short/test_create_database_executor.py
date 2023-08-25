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

from evadb.server.command_handler import execute_query_fetch_all


class CreateDatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()

    def test_create_database_should_add_the_entry(self):
        params = {
            "user": "user",
            "password": "password",
            "host": "127.0.0.1",
            "port": "5432",
            "database": "demo",
        }
        query = """CREATE DATABASE demo_db
                    WITH ENGINE = "postgres",
                    PARAMETERS = {};""".format(
            params
        )

        execute_query_fetch_all(self.evadb, query)

        db_entry = self.evadb.catalog().get_database_catalog_entry("demo_db")
        self.assertEqual(db_entry.name, "demo_db")
        self.assertEqual(db_entry.engine, "postgres")
        self.assertEqual(db_entry.params, params)


if __name__ == "__main__":
    unittest.main()
