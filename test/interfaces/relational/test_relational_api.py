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
import unittest
from test.markers import qdrant_skip_marker
from test.util import (
    DummyObjectDetector,
    create_sample_video,
    load_udfs_for_testing,
    shutdown_ray,
    suffix_pytest_xdist_worker_id_to_dir,
)

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from evadb.binder.binder_utils import BinderError
from evadb.configuration.constants import EvaDB_DATABASE_DIR, EvaDB_ROOT_DIR
from evadb.executor.executor_utils import ExecutorError
from evadb.interfaces.relational.db import connect
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all


class RelationalAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
        cls.conn = connect(cls.db_dir)
        cls.evadb = cls.conn._evadb

    def setUp(self):
        self.evadb.catalog().reset()
        self.mnist_path = f"{EvaDB_ROOT_DIR}/data/mnist/mnist.mp4"
        load_udfs_for_testing(
            self.evadb,
        )
        self.images = f"{EvaDB_ROOT_DIR}/data/detoxify/*.jpg"

    def tearDown(self):
        shutdown_ray()
        # todo: move these to relational apis as well
        execute_query_fetch_all(self.evadb, """DROP TABLE IF EXISTS mnist_video;""")
        execute_query_fetch_all(self.evadb, """DROP TABLE IF EXISTS meme_images;""")

    def test_relation_apis(self):
        cursor = self.conn.cursor()
        rel = cursor.load(
            self.mnist_path,
            table_name="mnist_video",
            format="video",
        )
        rel.execute()

        rel = cursor.table("mnist_video")
        assert_frame_equal(rel.df(), cursor.query("select * from mnist_video;").df())

        rel = rel.select("_row_id, id, data")
        assert_frame_equal(
            rel.df(),
            cursor.query("select _row_id, id, data from mnist_video;").df(),
        )

        rel = rel.filter("id < 10")
        assert_frame_equal(
            rel.df(),
            cursor.query(
                "select _row_id, id, data from mnist_video where id < 10;"
            ).df(),
        )

        rel = (
            rel.cross_apply("unnest(MnistImageClassifier(data))", "mnist(label)")
            .filter("mnist.label = 1")
            .select("_row_id, id")
        )

        query = """ select _row_id, id
                    from mnist_video
                        join lateral unnest(MnistImageClassifier(data)) AS mnist(label)
                    where id < 10 AND mnist.label = 1;"""
        assert_frame_equal(rel.df(), cursor.query(query).df())

        rel = cursor.load(
            self.images,
            table_name="meme_images",
            format="image",
        )
        rel.execute()

        rel = cursor.table("meme_images").select("_row_id, name")
        assert_frame_equal(
            rel.df(), cursor.query("select _row_id, name from meme_images;").df()
        )

        rel = rel.filter("_row_id < 3")
        assert_frame_equal(
            rel.df(),
            cursor.query(
                "select _row_id, name from meme_images where _row_id < 3;"
            ).df(),
        )

    def test_relation_api_chaining(self):
        cursor = self.conn.cursor()

        rel = cursor.load(
            self.mnist_path,
            table_name="mnist_video",
            format="video",
        )
        rel.execute()

        rel = (
            cursor.table("mnist_video")
            .select("id, data")
            .filter("id > 10")
            .filter("id < 20")
        )
        assert_frame_equal(
            rel.df(),
            cursor.query(
                "select id, data from mnist_video where id > 10 AND id < 20;"
            ).df(),
        )

    def test_interleaving_calls(self):
        cursor = self.conn.cursor()

        rel = cursor.load(
            self.mnist_path,
            table_name="mnist_video",
            format="video",
        )
        rel.execute()

        rel = cursor.table("mnist_video")
        filtered_rel = rel.filter("id > 10")

        assert_frame_equal(
            rel.filter("id > 10").df(),
            cursor.query("select * from mnist_video where id > 10;").df(),
        )

        assert_frame_equal(
            filtered_rel.select("_row_id, id").df(),
            cursor.query("select _row_id, id from mnist_video where id > 10;").df(),
        )

    @qdrant_skip_marker
    def test_create_index(self):
        cursor = self.conn.cursor()

        # load some images
        rel = cursor.load(
            self.images,
            table_name="meme_images",
            format="image",
        )
        rel.execute()

        # todo support register udf
        cursor.query(
            f"""CREATE UDF IF NOT EXISTS SiftFeatureExtractor
                IMPL  '{EvaDB_ROOT_DIR}/evadb/udfs/sift_feature_extractor.py'"""
        ).df()

        # create a vector index using QDRANT
        cursor.create_vector_index(
            "faiss_index",
            table_name="meme_images",
            expr="SiftFeatureExtractor(data)",
            using="QDRANT",
        ).df()

        # do similarity search
        base_image = f"{EvaDB_ROOT_DIR}/data/detoxify/meme1.jpg"
        rel = (
            cursor.table("meme_images")
            .order(
                f"Similarity(SiftFeatureExtractor(Open('{base_image}')), SiftFeatureExtractor(data))"
            )
            .limit(1)
            .select("name")
        )
        similarity_sql = """SELECT name FROM meme_images
                            ORDER BY
                                Similarity(SiftFeatureExtractor(Open("{}")), SiftFeatureExtractor(data))
                            LIMIT 1;""".format(
            base_image
        )
        assert_frame_equal(rel.df(), cursor.query(similarity_sql).df())

    def test_create_udf_with_relational_api(self):
        video_file_path = create_sample_video(10)

        cursor = self.conn.cursor()
        # load video
        rel = cursor.load(
            video_file_path,
            table_name="dummy_video",
            format="video",
        )
        rel.execute()

        create_dummy_object_detector_udf = cursor.create_function(
            "DummyObjectDetector", if_not_exists=True, impl_path="test/util.py"
        )
        create_dummy_object_detector_udf.execute()

        args = {"task": "automatic-speech-recognition", "model": "openai/whisper-base"}

        create_speech_recognizer_udf_if_not_exists = cursor.create_function(
            "SpeechRecognizer", if_not_exists=True, type="HuggingFace", **args
        )
        query = create_speech_recognizer_udf_if_not_exists.sql_query()
        self.assertEqual(
            query,
            """CREATE UDF IF NOT EXISTS SpeechRecognizer TYPE HuggingFace 'task' 'automatic-speech-recognition' 'model' 'openai/whisper-base'""",
        )
        create_speech_recognizer_udf_if_not_exists.execute()

        # check if next create call of same UDF raises error
        create_speech_recognizer_udf = cursor.create_function(
            "SpeechRecognizer", if_not_exists=False, type="HuggingFace", **args
        )
        query = create_speech_recognizer_udf.sql_query()
        self.assertEqual(
            query,
            "CREATE UDF SpeechRecognizer TYPE HuggingFace 'task' 'automatic-speech-recognition' 'model' 'openai/whisper-base'",
        )
        with self.assertRaises(ExecutorError):
            create_speech_recognizer_udf.execute()

        select_query_sql = (
            "SELECT id, DummyObjectDetector(data) FROM dummy_video ORDER BY id;"
        )
        actual_batch = cursor.query(select_query_sql).execute()
        labels = DummyObjectDetector().labels
        expected = [
            {
                "dummy_video.id": i,
                "dummyobjectdetector.label": np.array([labels[1 + i % 2]]),
            }
            for i in range(10)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    def test_drop_with_relational_api(self):
        video_file_path = create_sample_video(10)

        cursor = self.conn.cursor()
        # load video
        rel = cursor.load(
            video_file_path,
            table_name="dummy_video",
            format="video",
        )
        rel.execute()

        # Create dummy udf
        create_dummy_object_detector_udf = cursor.create_function(
            "DummyObjectDetector", if_not_exists=True, impl_path="test/util.py"
        )
        create_dummy_object_detector_udf.execute()

        # drop dummy udf
        drop_dummy_object_detector_udf = cursor.drop_function(
            "DummyObjectDetector", if_exists=True
        )
        drop_dummy_object_detector_udf.execute()

        # Check if deleted successfully
        select_query_sql = (
            "SELECT id, DummyObjectDetector(data) FROM dummy_video ORDER BY id;"
        )
        with self.assertRaises(BinderError):
            cursor.query(select_query_sql).execute()

        # drop non existing udf with if_exists=True should not raise error
        drop_dummy_object_detector_udf = cursor.drop_function(
            "DummyObjectDetector", if_exists=True
        )
        drop_dummy_object_detector_udf.execute()

        # if_exists=False should raise error
        drop_dummy_object_detector_udf = cursor.drop_function(
            "DummyObjectDetector", if_exists=False
        )
        with self.assertRaises(ExecutorError):
            drop_dummy_object_detector_udf.execute()

        # drop existing table
        drop_table = cursor.drop_table("dummy_video", if_exists=True)
        drop_table.execute()

        # Check if deleted successfully
        select_query_sql = "SELECT id, data FROM dummy_video ORDER BY id;"
        with self.assertRaises(BinderError):
            cursor.query(select_query_sql).execute()

        # drop non existing table with if_exists=True should not raise error
        drop_table = cursor.drop_table("dummy_video", if_exists=True)
        drop_table.execute()

        # if_exists=False should raise error
        drop_table = cursor.drop_table("dummy_video", if_exists=False)
        with self.assertRaises(ExecutorError):
            drop_table.execute()

    def test_pdf_similarity_search(self):
        conn = connect()
        cursor = conn.cursor()
        pdf_path = f"{EvaDB_ROOT_DIR}/data/documents/state_of_the_union.pdf"

        load_pdf = cursor.load(file_regex=pdf_path, format="PDF", table_name="PDFs")
        load_pdf.execute()

        udf_check = cursor.drop_function("SentenceFeatureExtractor")
        udf_check.df()
        udf = cursor.create_function(
            "SentenceFeatureExtractor",
            True,
            f"{EvaDB_ROOT_DIR}/evadb/udfs/sentence_feature_extractor.py",
        )
        udf.execute()

        cursor.create_vector_index(
            "faiss_index",
            table_name="PDFs",
            expr="SentenceFeatureExtractor(data)",
            using="FAISS",
        ).df()

        query = (
            cursor.table("PDFs")
            .order(
                """Similarity(
                    SentenceFeatureExtractor('When was the NATO created?'), SentenceFeatureExtractor(data)
                ) DESC"""
            )
            .limit(3)
            .select("data")
        )
        output = query.df()
        self.assertEqual(len(output), 3)
        self.assertTrue("pdfs.data" in output.columns)

        cursor.drop_index("faiss_index").df()

    def test_langchain_split_doc(self):
        conn = connect()
        cursor = conn.cursor()
        pdf_path1 = f"{EvaDB_ROOT_DIR}/data/documents/state_of_the_union.pdf"

        load_pdf = cursor.load(
            file_regex=pdf_path1, format="DOCUMENT", table_name="docs"
        )
        load_pdf.execute()

        result1 = (
            cursor.table("docs", chunk_size=2000, chunk_overlap=0).select("data").df()
        )

        result2 = (
            cursor.table("docs", chunk_size=4000, chunk_overlap=2000)
            .select("data")
            .df()
        )

        self.assertEqual(len(result1), len(result2))

        result1 = cursor.table("docs").select("data").df()

        result2 = cursor.query(
            "SELECT data from docs chunk_size 4000 chunk_overlap 200"
        ).df()
        self.assertEqual(len(result1), len(result2))

    def test_show_relational(self):
        video_file_path = create_sample_video(10)

        cursor = self.conn.cursor()
        # load video
        rel = cursor.load(
            video_file_path,
            table_name="dummy_video",
            format="video",
        )
        rel.execute()

        result = cursor.show("tables").df()
        self.assertEqual(len(result), 1)
        self.assertEqual(result["name"][0], "dummy_video")

    def test_explain_relational(self):
        video_file_path = create_sample_video(10)

        cursor = self.conn.cursor()
        # load video
        rel = cursor.load(
            video_file_path,
            table_name="dummy_video",
            format="video",
        )
        rel.execute()

        result = cursor.explain("SELECT * FROM dummy_video").df()
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0][0],
            "|__ ProjectPlan\n    |__ SeqScanPlan\n        |__ StoragePlan\n",
        )

    def test_rename_relational(self):
        video_file_path = create_sample_video(10)

        cursor = self.conn.cursor()
        # load video
        rel = cursor.load(
            video_file_path,
            table_name="dummy_video",
            format="video",
        )
        rel.execute()

        cursor.rename("dummy_video", "dummy_video_renamed").df()

        result = cursor.show("tables").df()

        self.assertEqual(len(result), 1)
        self.assertEqual(result["name"][0], "dummy_video_renamed")

    def test_create_table_relational(self):
        cursor = self.conn.cursor()

        cursor.create_table(
            table_name="dummy_table",
            if_not_exists=True,
            columns="id INTEGER, name text(30)",
        ).df()

        result = cursor.show("tables").df()

        self.assertEqual(len(result), 1)
        self.assertEqual(result["name"][0], "dummy_table")

        # if_not_exists=True should not raise error
        # rel = cursor.create_table(table_name="dummy_table", if_not_exists=True, columns="id INTEGER, name text(30)")
        # rel.execute()

        # if_not_exists=False should raise error
        rel = cursor.create_table(
            table_name="dummy_table",
            if_not_exists=False,
            columns="id INTEGER, name text(30)",
        )
        with self.assertRaises(ExecutorError):
            rel.execute()


if __name__ == "__main__":
    unittest.main()
