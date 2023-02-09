# coding=utf-8
# Copyright 2018-2022 EVA
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
import os
import unittest
import pytest

from test.util import (
    create_dummy_batches,
    create_dummy_csv_batches,
    create_sample_csv,
    create_sample_video,
    file_remove,
)

import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all
from eva.storage.storage_engine import StorageEngine
from pathlib import Path
from eva.configuration.constants import EVA_ROOT_DIR
EVA_INSTALLATION_DIR = ConfigurationManager().get_value("core", "eva_installation_dir")


from test.util import create_sample_image, load_inbuilt_udfs

class FuzzyJoinTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        self.video_file_path = create_sample_video()
        self.image_files_path = Path(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/*.jpg"
        )
        create_sample_csv()
        

        # Prepare needed UDFs and data.
        # load_inbuilt_udfs()
        # create_sample_image()
         # loading a csv requires a table to be created first
        create_table_query = """

            CREATE TABLE IF NOT EXISTS MyVideoCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER,
                video_id INTEGER,
                dataset_name TEXT(30),
                label TEXT(30),
                bbox NDARRAY FLOAT32(4),
                object_id INTEGER
            );
            """
        execute_query_fetch_all(create_table_query)

        # load the CSV
        load_query = """LOAD CSV 'dummy.csv' INTO MyVideoCSV;"""
        execute_query_fetch_all(load_query)

        # load the video to be joined with the csv
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(query)

    def tearDown(self):
        file_remove("dummy.avi")
        # file_remove("dummy.csv")
        # clean up
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")
        
    @pytest.mark.torchtest
    def test_fuzzyjoin(self):

        print(EVA_INSTALLATION_DIR)
        ocr_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
      INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
      OUTPUT (labels NDARRAY STR(10), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                scores NDARRAY FLOAT32(ANYDIM))
      TYPE  OCRExtraction
      IMPL  '{}/udfs/ocr_extractor.py';
      """.format(
    EVA_INSTALLATION_DIR
)

        fuzzy_udf = """CREATE UDF IF NOT EXISTS FuzzyJoin
                    INPUT (Input_Array1 NDARRAY ANYTYPE, Input_Array2 NDARRAY ANYTYPE)
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayUDF
                    IMPL "{}/udfs/{}/fuzzy_join.py";
        """.format(
    EVA_INSTALLATION_DIR, "ndarray"
)

        Crop_udf_query = """CREATE UDF IF NOT EXISTS Crop
                INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM),
                        bboxes NDARRAY FLOAT32(ANYDIM, 4))
                OUTPUT (Cropped_Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE  NdarrayUDF
                IMPL  "{}/udfs/{}/crop.py";
        """.format(
    EVA_INSTALLATION_DIR, "ndarray"
)

        mnist = f"{EVA_ROOT_DIR}/data/mnist/mnist.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{mnist}' INTO MNIST;")

        execute_query_fetch_all(ocr_udf_query)
        execute_query_fetch_all(fuzzy_udf)
        execute_query_fetch_all(Crop_udf_query)

        actual_batch1 = execute_query_fetch_all("SELECT * FROM MNIST;")
        print(actual_batch1.frames.columns)
        actual_batch2 = execute_query_fetch_all("SELECT * FROM MyVideoCSV;")
        print(actual_batch2.frames.columns)

        # select_query = """SELECT A.id, B.id FROM MyVideo A JOIN 
        #                MyVideoCSV B;"""

        select_query = """SELECT * FROM MyVideo a JOIN MyVideoCSV b
                      ON FuzzyJoin(b.label, b.label) < 1;"""

        # select_query = """SELECT * FROM MyVideo a JOIN MyVideoCSV b
        #               ON a.id = b.id;"""

        actual_batch = execute_query_fetch_all(select_query)

        print(actual_batch.frames.columns)



       
