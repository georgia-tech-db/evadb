import unittest

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

from test.util import create_sample_video, file_remove


class TrucateExecutorTest(unittest.TestCase):

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()

    def tearDown(self):
        file_remove('dummy.avi')

    # integration test
    def test_should_truncate_video_in_table(self):
        query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(query)

        trucate_query = """TRUNCATE TABLE MyVideo;"""
        execute_query_fetch_all(trucate_query)
