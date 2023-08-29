# this file tests the fetch, post and delete functions for slack integration
# will be adding a complete 'SQLAlchemy to slack' middleware later
# then this will be updated

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
from evadb.configuration.configuration_manager import ConfigurationManager

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
        batch = execute_query_fetch_all(self.evadb, query)
        print(batch)

