# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from test.markers import (
    gpu_skip_marker,
    ocr_skip_marker,
    ray_skip_marker,
    windows_skip_marker,
)
from test.util import (
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    load_udfs_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas.testing as pd_testing
import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all
from evadb.udfs.udf_bootstrap_queries import Asl_udf_query, Mvit_udf_query
from evadb.utils.generic_utils import try_to_import_cv2


@pytest.mark.notparallel
class PytorchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
        os.environ["ray"] = str(cls.evadb.config.get_value("experimental", "ray"))

        ua_detrac = f"{EvaDB_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        mnist = f"{EvaDB_ROOT_DIR}/data/mnist/mnist.mp4"
        actions = f"{EvaDB_ROOT_DIR}/data/actions/actions.mp4"
        asl_actions = f"{EvaDB_ROOT_DIR}/data/actions/computer_asl.mp4"
        meme1 = f"{EvaDB_ROOT_DIR}/data/detoxify/meme1.jpg"
        meme2 = f"{EvaDB_ROOT_DIR}/data/detoxify/meme2.jpg"

        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{mnist}' INTO MNIST;")
        execute_query_fetch_all(cls.evadb, f"LOAD VIDEO '{actions}' INTO Actions;")
        execute_query_fetch_all(
            cls.evadb, f"LOAD VIDEO '{asl_actions}' INTO Asl_actions;"
        )
        execute_query_fetch_all(cls.evadb, f"LOAD IMAGE '{meme1}' INTO MemeImages;")
        execute_query_fetch_all(cls.evadb, f"LOAD IMAGE '{meme2}' INTO MemeImages;")
        load_udfs_for_testing(cls.evadb)

    @classmethod
    def tearDownClass(cls):
        file_remove("ua_detrac.mp4")
        file_remove("mnist.mp4")
        file_remove("actions.mp4")
        file_remove("computer_asl.mp4")

        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS Actions;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MNIST;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS Asl_actions;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MemeImages;")

    def assertBatchEqual(self, a: Batch, b: Batch, msg: str):
        try:
            pd_testing.assert_frame_equal(a.frames, b.frames)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        self.addTypeEqualityFunc(Batch, self.assertBatchEqual)

    def tearDown(self) -> None:
        shutdown_ray()

    @ray_skip_marker
    def test_should_apply_parallel_match_sequential(self):
        # Parallel execution
        select_query = """SELECT id, obj.labels
                          FROM MyVideo JOIN LATERAL
                          FastRCNNObjectDetector(data)
                          AS obj(labels, bboxes, scores)
                         WHERE id < 20;"""
        par_batch = execute_query_fetch_all(self.evadb, select_query)

        # Sequential execution.
        self.evadb.config.update_value("experimental", "ray", False)
        select_query = """SELECT id, obj.labels
                          FROM MyVideo JOIN LATERAL
                          FastRCNNObjectDetector(data)
                          AS obj(labels, bboxes, scores)
                         WHERE id < 20;"""
        seq_batch = execute_query_fetch_all(self.evadb, select_query)
        # Recover configuration back.
        self.evadb.config.update_value("experimental", "ray", True)

        self.assertEqual(len(par_batch), len(seq_batch))
        self.assertEqual(par_batch, seq_batch)

    @ray_skip_marker
    def test_should_project_parallel_match_sequential(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS FaceDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  FaceDetection
                  IMPL  'evadb/udfs/face_detector.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = "SELECT FaceDetector(data) FROM MyVideo WHERE id < 5;"
        # Parallel execution
        par_batch = execute_query_fetch_all(self.evadb, select_query)

        # Sequential execution.
        self.evadb.config.update_value("experimental", "ray", False)
        seq_batch = execute_query_fetch_all(self.evadb, select_query)
        # Recover configuration back.
        self.evadb.config.update_value("experimental", "ray", True)

        self.assertEqual(len(par_batch), len(seq_batch))
        self.assertEqual(par_batch, seq_batch)

    def test_should_raise_exception_with_parallel(self):
        # Deliberately cause error.
        video_path = create_sample_video(100)
        load_query = f"LOAD VIDEO '{video_path}' INTO parallelErrorVideo;"
        execute_query_fetch_all(self.evadb, load_query)
        file_remove("dummy.avi")

        select_query = """SELECT id, obj.labels
                          FROM parallelErrorVideo JOIN LATERAL
                          FastRCNNObjectDetector(data)
                          AS obj(labels, bboxes, scores)
                         WHERE id < 2;"""
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(
                self.evadb, select_query, do_not_print_exceptions=True
            )

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_fastrcnn_with_lateral_join(self):
        select_query = """SELECT id, obj.labels
                          FROM MyVideo JOIN LATERAL
                          FastRCNNObjectDetector(data)
                          AS obj(labels, bboxes, scores)
                         WHERE id < 2;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 2)

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_yolo_and_mvit(self):
        execute_query_fetch_all(self.evadb, Mvit_udf_query)

        select_query = """SELECT FIRST(id),
                            Yolo(FIRST(data)),
                            MVITActionRecognition(SEGMENT(data))
                            FROM Actions
                            WHERE id < 32
                            GROUP BY '16 frames'; """
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 2)

        res = actual_batch.frames
        for idx in res.index:
            self.assertTrue(
                "person" in res["yolo.labels"][idx]
                and "yoga" in res["mvitactionrecognition.labels"][idx]
            )

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_asl(self):
        execute_query_fetch_all(self.evadb, Asl_udf_query)
        select_query = """SELECT FIRST(id), ASLActionRecognition(SEGMENT(data))
                        FROM Asl_actions
                        SAMPLE 5
                        GROUP BY '16 frames';"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        res = actual_batch.frames

        self.assertEqual(len(res), 1)
        for idx in res.index:
            self.assertTrue("computer" in res["aslactionrecognition.labels"][idx])

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_facenet(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS FaceDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  FaceDetection
                  IMPL  'evadb/udfs/face_detector.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = """SELECT FaceDetector(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 5)

    @pytest.mark.torchtest
    @windows_skip_marker
    @ocr_skip_marker
    def test_should_run_pytorch_and_ocr(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'evadb/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = """SELECT OCRExtractor(data) FROM MNIST
                        WHERE id >= 150 AND id < 155;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 5)

        # non-trivial test case for MNIST
        res = actual_batch.frames
        self.assertTrue(res["ocrextractor.labels"][0][0] == "4")
        self.assertTrue(res["ocrextractor.scores"][2][0] > 0.9)

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_resnet50(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS FeatureExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (features NDARRAY FLOAT32(ANYDIM))
                  TYPE  Classification
                  IMPL  'evadb/udfs/feature_extractor.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = """SELECT FeatureExtractor(data) FROM MyVideo
                        WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 5)

        # non-trivial test case for Resnet50
        res = actual_batch.frames
        self.assertEqual(res["featureextractor.features"][0].shape, (1, 2048))
        # self.assertTrue(res["featureextractor.features"][0][0][0] > 0.3)

    @pytest.mark.torchtest
    def test_should_run_pytorch_and_similarity(self):
        create_open_udf_query = """CREATE UDF IF NOT EXISTS Open
                INPUT (img_path TEXT(1000))
                OUTPUT (data NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE NdarrayUDF
                IMPL "evadb/udfs/ndarray/open.py";
        """
        execute_query_fetch_all(self.evadb, create_open_udf_query)

        create_similarity_udf_query = """CREATE UDF IF NOT EXISTS Similarity
                    INPUT (Frame_Array_Open NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Frame_Array_Base NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Feature_Extractor_Name TEXT(100))
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayUDF
                    IMPL "evadb/udfs/ndarray/similarity.py";
        """
        execute_query_fetch_all(self.evadb, create_similarity_udf_query)

        create_feat_udf_query = """CREATE UDF IF NOT EXISTS FeatureExtractor
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (features NDARRAY FLOAT32(ANYDIM))
                  TYPE  Classification
                  IMPL  "evadb/udfs/feature_extractor.py";
        """
        execute_query_fetch_all(self.evadb, create_feat_udf_query)

        select_query = """SELECT data FROM MyVideo WHERE id = 1;"""
        batch_res = execute_query_fetch_all(self.evadb, select_query)
        img = batch_res.frames["myvideo.data"][0]

        tmp_dir_from_config = self.evadb.config.get_value("storage", "tmp_dir")

        img_save_path = os.path.join(tmp_dir_from_config, "dummy.jpg")
        try:
            os.remove(img_save_path)
        except FileNotFoundError:
            pass

        try_to_import_cv2()
        import cv2

        cv2.imwrite(img_save_path, img)

        similarity_query = """SELECT data FROM MyVideo WHERE id < 5
                    ORDER BY Similarity(FeatureExtractor(Open("{}")),
                                        FeatureExtractor(data))
                    LIMIT 1;""".format(
            img_save_path
        )
        actual_batch = execute_query_fetch_all(self.evadb, similarity_query)

        similar_data = actual_batch.frames["myvideo.data"][0]
        self.assertTrue(np.array_equal(img, similar_data))

    @pytest.mark.torchtest
    @windows_skip_marker
    @ocr_skip_marker
    def test_should_run_ocr_on_cropped_data(self):
        create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                  INPUT  (text NDARRAY STR(100))
                  OUTPUT (labels NDARRAY STR(10),
                          bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  OCRExtraction
                  IMPL  'evadb/udfs/ocr_extractor.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = """SELECT OCRExtractor(Crop(data, [2, 2, 24, 24])) FROM MNIST
                        WHERE id >= 150 AND id < 155;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 5)

        # non-trivial test case for MNIST
        res = actual_batch.frames
        self.assertTrue(res["ocrextractor.labels"][0][0] == "4")
        self.assertTrue(res["ocrextractor.scores"][2][0] > 0.9)

    @pytest.mark.torchtest
    @gpu_skip_marker
    def test_should_run_extract_object(self):
        select_query = """
            SELECT id, T.iids, T.bboxes, T.scores, T.labels
            FROM MyVideo JOIN LATERAL EXTRACT_OBJECT(data, Yolo, NorFairTracker)
                AS T(iids, labels, bboxes, scores)
            WHERE id < 30;
            """
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(actual_batch), 30)

        num_of_entries = actual_batch.frames["T.iids"].apply(lambda x: len(x)).sum()

        select_query = """
            SELECT id, T.iid, T.bbox, T.score, T.label
            FROM MyVideo JOIN LATERAL
                UNNEST(EXTRACT_OBJECT(data, Yolo, NorFairTracker)) AS T(iid, label, bbox, score)
            WHERE id < 30;
            """
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        # do some more meaningful check
        self.assertEqual(len(actual_batch), num_of_entries)

    def test_check_unnest_with_predicate_on_yolo(self):
        query = """SELECT id, Yolo.label, Yolo.bbox, Yolo.score
                  FROM MyVideo
                  JOIN LATERAL UNNEST(Yolo(data)) AS Yolo(label, bbox, score)
                  WHERE Yolo.label = 'car' AND id < 2;"""

        actual_batch = execute_query_fetch_all(self.evadb, query)

        # due to unnest the number of returned tuples should be at least > 10
        self.assertTrue(len(actual_batch) > 2)


if __name__ == "__main__":
    unittest.main()
