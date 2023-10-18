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
from test.util import get_evadb_for_testing

import pytest

from evadb.server.command_handler import execute_query_fetch_all
from evadb.third_party.databases.github.table_column_info import STARGAZERS_COLUMNS


@pytest.mark.notparallel
class GithubDataSourceTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

    def tearDown(self):
        execute_query_fetch_all(self.evadb, "DROP DATABASE IF EXISTS github_data;")

    @pytest.mark.skip(
        reason="Need https://github.com/georgia-tech-db/evadb/pull/1280 for a cost-based rebatch optimization"
    )
    @pytest.mark.xfail(reason="Flaky testcase due to `bad request` error message")
    def test_should_run_select_query_in_github(self):
        # Create database.
        params = {
            "owner": "georgia-tech-db",
            "repo": "evadb",
        }
        query = f"""CREATE DATABASE github_data
                    WITH ENGINE = "github",
                    PARAMETERS = {params};"""
        execute_query_fetch_all(self.evadb, query)

        query = "SELECT * FROM github_data.stargazers LIMIT 10;"
        batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(batch), 10)
        expected_column = list(
            ["stargazers.{}".format(col) for col, _ in STARGAZERS_COLUMNS]
        )
        self.assertEqual(batch.columns, expected_column)


if __name__ == "__main__":
    unittest.main()
