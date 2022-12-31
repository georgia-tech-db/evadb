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
import sys
import unittest
from test.util import copy_sample_videos_to_upload_dir, file_remove, load_inbuilt_udfs

import cv2
import numpy as np
import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.udf_bootstrap_queries import Mvit_udf_query


class PytorchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        copy_sample_videos_to_upload_dir()
        ua_detrac = f"{EVA_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        mnist = f"{EVA_ROOT_DIR}/data/mnist/mnist.mp4"
        actions = f"{EVA_ROOT_DIR}/data/actions/actions.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        execute_query_fetch_all(f"LOAD VIDEO '{mnist}' INTO MNIST;")
        execute_query_fetch_all(f"LOAD VIDEO '{actions}' INTO Actions;")
        load_inbuilt_udfs()

    @classmethod
    def tearDownClass(cls):
        file_remove("ua_detrac.mp4")
        file_remove("mnist.mp4")
        file_remove("actions.mp4")
        execute_query_fetch_all("DROP TABLE IF EXISTS Actions;")
        execute_query_fetch_all("DROP TABLE IF EXISTS Mnist;")
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_fastrcnn(self):
        select_query = """SELECT FastRCNNObjectDetector(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 5)

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_yolo(self):
        select_query = """SELECT YoloV5(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 5)

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_mvit(self):

        execute_query_fetch_all(Mvit_udf_query)
        select_query = """SELECT FIRST(id), MVITActionRecognition(SEGMENT(data)) FROM Actions
                       GROUP BY '16f';"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 9)
        res = actual_batch.frames
        # TODO ACTION: Test case for aliases
        for idx in res.index:
            self.assertTrue("yoga" in res["mvitactionrecognition.labels"][idx])

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_fastrcnn_and_mvit(self):
        execute_query_fetch_all(Mvit_udf_query)

        select_query = """SELECT FIRST(id),
                                 YoloV5(FIRST(data)),
                                 MVITActionRecognition(SEGMENT(data))
                       FROM Actions
                       GROUP BY '16f';"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 9)

        res = actual_batch.frames
        for idx in res.index:
            self.assertTrue(
                "person" in res["yolov5.labels"][idx]
                and "yoga" in res["mvitactionrecognition.labels"][idx]
            )

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_facenet(self):
        create_udf_query = """CREATE UDF FaceDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  FaceDetection
                  IMPL  'eva/udfs/face_detector.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT FaceDetector(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 5)

    @pytest.mark.torchtest
    @pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
    def test_should_run_pytorch_and_ocr(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'eva/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT OCRExtractor(data) FROM MNIST
                        WHERE id >= 150 AND id < 155;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 5)

        # non-trivial test case for MNIST
        res = actual_batch.frames
        self.assertTrue(res["ocrextractor.labels"][0][0] == "4")
        self.assertTrue(res["ocrextractor.scores"][2][0] > 0.9)

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_resnet50(self):
        create_udf_query = """CREATE UDF FeatureExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (features NDARRAY FLOAT32(ANYDIM))
                  TYPE  Classification
                  IMPL  'eva/udfs/feature_extractor.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT FeatureExtractor(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 5)

        # non-trivial test case for Resnet50
        res = actual_batch.frames
        self.assertEqual(res["featureextractor.features"][0].shape, (1, 2048))
        self.assertTrue(res["featureextractor.features"][0][0][0] > 0.3)

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_similarity(self):
        create_open_udf_query = """CREATE UDF IF NOT EXISTS Open
                INPUT (img_path TEXT(1000))
                OUTPUT (data NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE NdarrayUDF
                IMPL "eva/udfs/ndarray/open.py";
        """
        execute_query_fetch_all(create_open_udf_query)

        create_similarity_udf_query = """CREATE UDF IF NOT EXISTS Similarity
                    INPUT (Frame_Array_Open NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Frame_Array_Base NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Feature_Extractor_Name TEXT(100))
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayUDF
                    IMPL "eva/udfs/ndarray/similarity.py";
        """
        execute_query_fetch_all(create_similarity_udf_query)

        create_feat_udf_query = """CREATE UDF IF NOT EXISTS FeatureExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (features NDARRAY FLOAT32(ANYDIM))
                  TYPE  Classification
                  IMPL  "eva/udfs/feature_extractor.py";
        """
        execute_query_fetch_all(create_feat_udf_query)

        select_query = """SELECT data FROM MyVideo WHERE id = 1;"""
        batch_res = execute_query_fetch_all(select_query)
        img = batch_res.frames["myvideo.data"][0]

        config = ConfigurationManager()
        upload_dir_from_config = config.get_value("storage", "upload_dir")

        img_save_path = os.path.join(upload_dir_from_config, "dummy.jpg")
        try:
            os.remove(img_save_path)
        except FileNotFoundError:
            pass
        cv2.imwrite(img_save_path, img)

        similarity_query = """SELECT data FROM MyVideo WHERE id < 5
                    ORDER BY Similarity(FeatureExtractor(Open("{}")),
                                        FeatureExtractor(data))
                    LIMIT 1;""".format(
            img_save_path
        )
        actual_batch = execute_query_fetch_all(similarity_query)

        similar_data = actual_batch.frames["myvideo.data"][0]
        self.assertTrue(np.array_equal(img, similar_data))

    @pytest.mark.torchtest
    @pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
    def test_should_run_ocr_on_cropped_data(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'eva/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(create_udf_query)

        select_query = """SELECT OCRExtractor(Crop(data, [2, 2, 24, 24])) FROM MNIST
                        WHERE id >= 150 AND id < 155;"""
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(len(actual_batch), 5)

        # non-trivial test case for MNIST
        res = actual_batch.frames
        self.assertTrue(res["ocrextractor.labels"][0][0] == "4")
        self.assertTrue(res["ocrextractor.scores"][2][0] > 0.9)
