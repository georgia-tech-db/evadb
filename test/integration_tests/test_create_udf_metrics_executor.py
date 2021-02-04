import os
import unittest

import numpy as np
import pandas as pd

from src.catalog.catalog_manager import CatalogManager
from src.models.storage.batch import Batch
from src.readers.opencv_reader import OpenCVReader
from test.util import create_sample_video, create_dummy_batches, perform_query


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
