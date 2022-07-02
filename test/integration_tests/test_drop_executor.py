import unittest

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

from test.util import create_sample_video, file_remove


class DropExecutorTest(unittest.TestCase):

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()

    def tearDown(self):
        file_remove('dummy.avi')

    # integration test
    def test_should_drop_table(self):
        query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(query)

        drop_query = """DROP TABLE MyVideo;"""
        execute_query_fetch_all(drop_query)
