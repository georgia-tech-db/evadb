from pathlib import Path
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
        file_remove("dummy.avi")

    # integration test
    def test_should_drop_table(self):
        catalog_manager = CatalogManager()
        query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(query)

        metadata_obj = catalog_manager.get_dataset_metadata(
            None, "MyVideo"
        )
        video_dir = metadata_obj.file_url
        self.assertFalse(metadata_obj is None)
        column_objects = catalog_manager.get_all_column_objects(metadata_obj)
        self.assertEqual(len(column_objects), 2)
        self.assertTrue(Path(video_dir).exists())
        drop_query = """DROP TABLE MyVideo;"""
        execute_query_fetch_all(drop_query)
        self.assertTrue(
            catalog_manager.get_dataset_metadata(None, "MyVideo") is None
        )
        column_objects = catalog_manager.get_all_column_objects(metadata_obj)
        self.assertEqual(len(column_objects), 0)
        self.assertFalse(Path(video_dir).exists())


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(DropExecutorTest(
        'test_should_drop_table'))
    unittest.TextTestRunner().run(suite)
