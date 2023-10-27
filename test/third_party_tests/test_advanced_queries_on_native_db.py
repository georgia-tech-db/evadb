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

# We only test thes eon sqlite in a hope that it would work for other databases.


@pytest.mark.notparallel
class NativeDbAdvancedTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

        # Create database.
        import os

        params = {
            "database": f"/home/gkakkar7/VAST/github-analyzer/stargazer.db",
        }
        query = f"""CREATE DATABASE sqlite_data
                    WITH ENGINE = "sqlite",
                    PARAMETERS = {params};"""
        execute_query_fetch_all(self.evadb, query)

    def tearDown(self):
        shutdown_ray()

    def test_queries(self):
        repo_url = "https://github.com/georgia-tech-db/evadb"
        parts = repo_url.strip("/").split("/")
        repo_name = parts[-1]
        github_pat = "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"

        query = """CREATE OR REPLACE FUNCTION GithubStargazers
            INPUT (repo_url TEXT(1000), github_pat TEXT(1000))
            OUTPUT (github_username NDARRAY STR(ANYDIM))
            TYPE  Webscraping
            IMPL  '/home/gkakkar7/VAST/github-analyzer/github_stargazers.py';"""

        execute_query_fetch_all(self.evadb, query)

        query = f"""
           CREATE TABLE IF NOT EXISTS sqlite_data.{repo_name}_StargazerList AS
           SELECT GithubStargazers("{repo_url}", "{github_pat}");
        """

        execute_query_fetch_all(self.evadb, query)

        query = f"SELECT * FROM sqlite_data.{repo_name}_StargazerList;"
        execute_query_fetch_all(self.evadb, query)


if __name__ == "__main__":
    unittest.main()
