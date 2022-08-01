import unittest

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all

from test.util import create_sample_video, file_remove


class RenameExecutorTest(unittest.TestCase):

    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        create_sample_video()

    def tearDown(self):
        file_remove('dummy.avi')

    # integration test
    def test_should_rename_table(self):
        catalog_manager = CatalogManager()
        query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(query)

        self.assertTrue(
            catalog_manager.get_dataset_metadata(None, "MyVideo") is not None
        )
        self.assertTrue(
            catalog_manager.get_dataset_metadata(None, "MyVideo1") is None
        )

        rename_query = """RENAME TABLE MyVideo TO MyVideo1;"""
        execute_query_fetch_all(rename_query)

        self.assertTrue(
            catalog_manager.get_dataset_metadata(None, "MyVideo") is None
        )
        self.assertTrue(
            catalog_manager.get_dataset_metadata(None, "MyVideo1") is not None
        )
