import unittest

from src.catalog.catalog_manager import CatalogManager
from src.server.command_handler import execute_query_fetch_all
from src.utils.metrics_manager import MetricsManager
from test.util import create_sample_video, file_remove

NUM_FRAMES = 10


class MetricsManagerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)

    @classmethod
    def tearDownClass(cls):
        file_remove('dummy.avi')

    def test_latency(self):
        mm = MetricsManager()

        select_query = "SELECT id, data FROM MyVideo WHERE id < 5;"
        execute_query_fetch_all(select_query, mm)

        self.assertEqual(mm.print().keys(), ["latency (ns)"])
        self.assertEqual(
            mm.print().keys()["latency (ns)"].keys(),
            ["parsing", "planning.convertor", "planning.build", "execution"])
