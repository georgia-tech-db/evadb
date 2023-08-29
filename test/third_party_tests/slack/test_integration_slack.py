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

"""
queries to test:
1) Create a database using slack engine
    CREATE DATABASE "slacktest"
        WITH ENGINE = "slack";

2) Fetch messages using get_messages() method
    SELECT * FROM slacktest.channels
    WHERE channel = "#test1"
    AND (QUERY)

3) Post messages using post_message() method
    INSERT INTO slacktest.channels (channel, message)
    VALUES
    ("#test1", "hello, world!"),
    (...);

4) Delete from the channel
    DELETE FROM slacktest.channels
    WHERE channel = "#test1" and ts = "12341235125.31543232";
"""
import unittest
from test.util import get_evadb_for_testing, shutdown_ray

from evadb.server.command_handler import execute_query_fetch_all


class CreateSlackDatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()

    def test_create_database_should_add_the_entry(self):
        query = """CREATE DATABASE demo_db
                    WITH ENGINE = "slack";"""

        execute_query_fetch_all(self.evadb, query)

        db_entry = self.evadb.catalog().get_database_catalog_entry("demo_db")
        self.assertEqual(db_entry.name, "demo_db")
        self.assertEqual(db_entry.engine, "slack")

    def test_select_database_should_get_slack_api(self):
        # TODO: get token from evadb.yml
        # Create a Database first
        query = """CREATE DATABASE demo_db
                    WITH ENGINE = "slack";"""

        execute_query_fetch_all(self.evadb, query)

        query = "SELECT * FROM demo_db.test1"
        execute_query_fetch_all(self.evadb, query)
