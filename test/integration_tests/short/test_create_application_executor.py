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

from mock import patch

from evadb.parser.lark_visitor._create_statements import App_Type
from evadb.server.command_handler import execute_query_fetch_all


class CreateApplicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()

    def test_create_application_should_add_the_entry(self):
        params = {
            "token": "xapp-1-A05PGEDKFHV-5813035563474-e52ef03f0b6d2600a6711db470382c59d0e40a91ad12a32402db5298730c55c6",
            "channel": "evadb-bot-testing",
            "open_ai_token": "abc123",
        }
        query = """CREATE APPLICATION example_app
                   WITH ENGINE = "slack",
                   PARAMETERS = {};""".format(
            params
        )
        with patch("evadb.executor.create_database_executor.get_database_handler"):
            execute_query_fetch_all(self.evadb, query)

        db_entry = self.evadb.catalog().get_database_catalog_entry("example_app")
        self.assertEqual(db_entry.name, "example_app")
        self.assertEqual(db_entry.app_type, App_Type.Application)
        self.assertEqual(db_entry.engine, "slack")
        self.assertEqual(db_entry.params, params)


if __name__ == "__main__":
    unittest.main()
