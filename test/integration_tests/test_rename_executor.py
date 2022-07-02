import unittest
import numpy as np

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all
from eva.utils.logging_manager import logger

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
        query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(query)

        rename_query = """RENAME TABLE MyVideo TO MyVideo2;"""
        execute_query_fetch_all(rename_query)