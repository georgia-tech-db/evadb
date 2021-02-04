import unittest

from src.catalog.catalog_manager import CatalogManager
from test.util import perform_query


class CreateUDFMetricsExecutorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        load_query = """CREATE UDF FastRCNNObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (label TEXT(10))
                  TYPE  Classification
                  IMPL  'src/udfs/fastrcnn_object_detector.py';
        """
        perform_query(load_query)

    def test_create_udf_metrics(self):
        query = """CREATE UDFMETRICS FastRCNNObjectDetector
                   DATASET 'COCO' CATEGORY 'Car'
                   PRECISION 0.6 RECALL 0.5;"""
        perform_query(query)
