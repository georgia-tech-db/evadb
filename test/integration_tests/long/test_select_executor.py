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
from test.util import (  # file_remove,
    create_dummy_batches,
    create_sample_video,
    create_table,
    file_remove,
    get_evadb_for_testing,
    load_udfs_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.models.storage.batch import Batch
from evadb.readers.decord_reader import DecordReader
from evadb.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


@pytest.mark.notparallel
class SelectExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
        video_file_path = create_sample_video(NUM_FRAMES)
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(cls.evadb, load_query)
        ua_detrac = f"{EvaDB_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        load_query = f"LOAD VIDEO '{ua_detrac}' INTO DETRAC;"
        execute_query_fetch_all(cls.evadb, load_query)
        load_udfs_for_testing(cls.evadb)
        cls.table1 = create_table(cls.evadb, "table1", 100, 3)
        cls.table2 = create_table(cls.evadb, "table2", 500, 3)
        cls.table3 = create_table(cls.evadb, "table3", 1000, 3)

        cls.meme1 = f"{EvaDB_ROOT_DIR}/data/detoxify/meme1.jpg"
        cls.meme2 = f"{EvaDB_ROOT_DIR}/data/detoxify/meme2.jpg"

        execute_query_fetch_all(cls.evadb, f"LOAD IMAGE '{cls.meme1}' INTO MemeImages;")
        execute_query_fetch_all(cls.evadb, f"LOAD IMAGE '{cls.meme2}' INTO MemeImages;")

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()

        file_remove("dummy.avi")
        execute_query_fetch_all(cls.evadb, """DROP TABLE IF EXISTS table1;""")
        execute_query_fetch_all(cls.evadb, """DROP TABLE IF EXISTS table2;""")
        execute_query_fetch_all(cls.evadb, """DROP TABLE IF EXISTS table3;""")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyVideo;")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MemeImages;")

    def test_should_load_and_select_real_audio_in_table(self):
        query = """LOAD VIDEO 'data/sample_videos/touchdown.mp4'
                   INTO TOUCHDOWN;"""
        execute_query_fetch_all(self.evadb, query)

        select_query = "SELECT id, audio FROM TOUCHDOWN;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort("touchdown.id")
        video_reader = DecordReader("data/sample_videos/touchdown.mp4", read_audio=True)
        expected_batch = Batch(frames=pd.DataFrame())
        for batch in video_reader.read():
            batch.frames["name"] = "touchdown.mp4"
            expected_batch += batch
        expected_batch.modify_column_alias("touchdown")
        expected_batch = expected_batch.project(["touchdown.id", "touchdown.audio"])
        self.assertEqual(actual_batch, expected_batch)

    def test_chunk_param_should_fail(self):
        with self.assertRaises(AssertionError):
            execute_query_fetch_all(
                self.evadb,
                "SELECT data from MyVideo chunk_size 4000 chunk_overlap 200;",
            )

        with self.assertRaises(AssertionError):
            execute_query_fetch_all(
                self.evadb,
                "SELECT data from MemeImages chunk_size 4000 chunk_overlap 200;",
            )

    @pytest.mark.torchtest
    def test_lateral_join(self):
        select_query = """SELECT id, a FROM DETRAC JOIN LATERAL
                        Yolo(data) AS T(a,b,c) WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(list(actual_batch.columns), ["detrac.id", "T.a"])
        self.assertEqual(len(actual_batch), 5)

    def test_complex_logical_expressions(self):
        query = """SELECT id FROM MyVideo
            WHERE DummyObjectDetector(data).label = ['{}']  ORDER BY id;"""
        persons = execute_query_fetch_all(
            self.evadb, query.format("person")
        ).frames.to_numpy()
        bicycles = execute_query_fetch_all(
            self.evadb, query.format("bicycle")
        ).frames.to_numpy()
        import numpy as np

        self.assertTrue(len(np.intersect1d(persons, bicycles)) == 0)

        query_or = """SELECT id FROM MyVideo \
            WHERE DummyObjectDetector(data).label = ['person']
                OR DummyObjectDetector(data).label = ['bicycle']
            ORDER BY id;"""
        actual = execute_query_fetch_all(self.evadb, query_or)
        expected = execute_query_fetch_all(
            self.evadb, "SELECT id FROM MyVideo ORDER BY id"
        )
        self.assertEqual(expected, actual)

        query_and = """SELECT id FROM MyVideo \
            WHERE DummyObjectDetector(data).label = ['person']
                AND DummyObjectDetector(data).label = ['bicycle']
            ORDER BY id;"""

        expected = execute_query_fetch_all(self.evadb, query_and)
        self.assertEqual(len(expected), 0)

    def test_select_and_union_video_in_table(self):
        select_query = """SELECT * FROM MyVideo WHERE id < 3
            UNION ALL SELECT * FROM MyVideo WHERE id > 7;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort("myvideo.id")
        expected_batch = list(
            create_dummy_batches(
                filters=[i for i in range(NUM_FRAMES) if i < 3 or i > 7]
            )
        )[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = """SELECT * FROM MyVideo WHERE id < 2
            UNION ALL SELECT * FROM MyVideo WHERE id > 4 AND id < 6
            UNION ALL SELECT * FROM MyVideo WHERE id > 7;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort("myvideo.id")
        expected_batch = list(
            create_dummy_batches(
                filters=[i for i in range(NUM_FRAMES) if i < 2 or i == 5 or i > 7]
            )
        )[0]
        self.assertEqual(actual_batch, expected_batch)

    def test_sort_on_nonprojected_column(self):
        """This tests doing an order by on a column
        that is not projected. The orderby_executor currently
        catches the KeyError, passes, and returns the untouched
        data
        """
        select_query = "SELECT data FROM MyVideo ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        select_query = "SELECT data FROM MyVideo"
        expected_batch = execute_query_fetch_all(self.evadb, select_query)

        self.assertEqual(len(actual_batch), len(expected_batch))

    def test_should_load_and_select_real_video_in_table(self):
        query = """LOAD VIDEO 'data/mnist/mnist.mp4'
                   INTO MNIST;"""
        execute_query_fetch_all(self.evadb, query)

        select_query = "SELECT id, data FROM MNIST;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort("mnist.id")
        video_reader = DecordReader("data/mnist/mnist.mp4")
        expected_batch = Batch(frames=pd.DataFrame())
        for batch in video_reader.read():
            batch.frames["name"] = "mnist.mp4"
            expected_batch += batch
        expected_batch.modify_column_alias("mnist")
        expected_batch = expected_batch.project(["mnist.id", "mnist.data"])
        self.assertEqual(actual_batch, expected_batch)

    def test_project_identifier_column(self):
        # test for video table
        batch = execute_query_fetch_all(self.evadb, "SELECT _row_id, id FROM MyVideo;")
        expected = Batch(
            pd.DataFrame(
                {
                    "myvideo._row_id": [1] * NUM_FRAMES,
                    "myvideo.id": range(NUM_FRAMES),
                }
            )
        )
        self.assertEqual(batch, expected)

        batch = execute_query_fetch_all(self.evadb, "SELECT * FROM MyVideo;")
        self.assertTrue("myvideo._row_id" in batch.columns)

        # test for image table
        batch = execute_query_fetch_all(
            self.evadb, "SELECT _row_id, name FROM MemeImages;"
        )
        expected = Batch(
            pd.DataFrame(
                {
                    "memeimages._row_id": [1, 2],
                    "memeimages.name": [self.meme1, self.meme2],
                }
            )
        )
        self.assertEqual(batch, expected)

        batch = execute_query_fetch_all(self.evadb, "SELECT * FROM MemeImages;")
        self.assertTrue("memeimages._row_id" in batch.columns)

        # test for structural table
        batch = execute_query_fetch_all(self.evadb, "SELECT _row_id FROM table1;")
        expected = Batch(
            pd.DataFrame(
                {
                    "table1._row_id": range(1, 101),
                }
            )
        )
        self.assertEqual(batch, expected)

        batch = execute_query_fetch_all(self.evadb, "SELECT * FROM table1;")
        self.assertTrue("table1._row_id" in batch.columns)

    def test_select_and_sample(self):
        select_query = "SELECT id FROM MyVideo SAMPLE 7 ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()

        expected_batch = list(create_dummy_batches(filters=range(0, NUM_FRAMES, 7)))
        expected_batch[0] = expected_batch[0].project(["myvideo.id"])

        self.assertEqual(len(actual_batch), len(expected_batch[0]))
        self.assertEqual(actual_batch, expected_batch[0])

    def test_select_and_where_video_in_table(self):
        select_query = "SELECT * FROM MyVideo WHERE id = 5;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected_batch = list(create_dummy_batches(filters=[5]))[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT data FROM MyVideo WHERE id = 5;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(actual_batch, expected_batch.project(["myvideo.data"]))

        select_query = "SELECT id, data FROM MyVideo WHERE id >= 2;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(2, NUM_FRAMES)))[0]
        self.assertEqual(
            actual_batch,
            expected_batch.project(["myvideo.id", "myvideo.data"]),
        )

        select_query = "SELECT * FROM MyVideo WHERE id >= 2 AND id < 5;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(2, 5)))[0]

        self.assertEqual(actual_batch, expected_batch)

    def test_hash_join_with_multiple_tables(self):
        select_query = """SELECT * FROM table1 JOIN table2
                          ON table2.a0 = table1.a0 JOIN table3
                          ON table3.a1 = table1.a1 WHERE table1.a2 > 50;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        tmp = pd.merge(
            self.table1,
            self.table2,
            left_on=["table1.a0"],
            right_on=["table2.a0"],
            how="inner",
        )
        expected = pd.merge(
            tmp,
            self.table3,
            left_on=["table1.a1"],
            right_on=["table3.a1"],
            how="inner",
        )
        expected = expected.where(expected["table1.a2"] > 50)
        if len(expected):
            expected_batch = Batch(expected)
            self.assertEqual(
                expected_batch.sort_orderby(["table1.a0"]),
                actual_batch.sort_orderby(["table1.a0"]),
            )

    def test_nested_select_video_in_table(self):
        nested_select_query = """SELECT * FROM
            (SELECT * FROM MyVideo WHERE id >= 2 AND id < 5) AS T
            WHERE id >= 3;"""
        actual_batch = execute_query_fetch_all(self.evadb, nested_select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(filters=range(3, 5)))[0]
        expected_batch.modify_column_alias("T")
        self.assertEqual(actual_batch, expected_batch)

        nested_select_query = """SELECT * FROM
            (SELECT * FROM MyVideo WHERE id >= 2 AND id < 5) AS T
            WHERE id >= 3;"""
        actual_batch = execute_query_fetch_all(self.evadb, nested_select_query)
        actual_batch.sort("T.id")
        expected_batch = list(create_dummy_batches(filters=range(3, 5)))[0]
        expected_batch.modify_column_alias("T")
        self.assertEqual(actual_batch, expected_batch)

    def test_select_and_sample_with_predicate(self):
        select_query = "SELECT id FROM MyVideo SAMPLE 2 WHERE id > 5 ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected_batch = list(create_dummy_batches(filters=range(6, NUM_FRAMES, 2)))
        self.assertEqual(actual_batch, expected_batch[0].project(["myvideo.id"]))

        select_query = "SELECT id FROM MyVideo SAMPLE 4 WHERE id > 2 ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected_batch = list(create_dummy_batches(filters=range(4, NUM_FRAMES, 4)))
        self.assertEqual(actual_batch, expected_batch[0].project(["myvideo.id"]))

        select_query = (
            "SELECT id FROM MyVideo SAMPLE 2 WHERE id > 2 AND id < 8 ORDER BY id;"
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected_batch = list(create_dummy_batches(filters=range(4, 8, 2)))
        self.assertEqual(actual_batch, expected_batch[0].project(["myvideo.id"]))

    def test_lateral_join_with_unnest_on_subset_of_outputs(self):
        query = """SELECT id, label
                  FROM MyVideo JOIN LATERAL
                    UNNEST(DummyMultiObjectDetector(data).labels) AS T(label)
                  WHERE id < 2 ORDER BY id;"""
        unnest_batch = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame(
                {
                    "myvideo.id": np.array([0, 0, 1, 1], np.intp),
                    "T.label": np.array(["person", "person", "bicycle", "bicycle"]),
                }
            )
        )
        self.assertEqual(unnest_batch, expected)

        # unnest with predicate on function expression
        query = """SELECT id, label
                FROM MyVideo JOIN LATERAL
                UNNEST(DummyMultiObjectDetector(data).labels) AS T(label)
                WHERE id < 2 AND T.label = "person" ORDER BY id;"""
        unnest_batch = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame(
                {
                    "myvideo.id": np.array([0, 0], np.intp),
                    "T.label": np.array(["person", "person"]),
                }
            )
        )
        self.assertEqual(unnest_batch, expected)

    def test_lateral_join_with_unnest(self):
        query = """SELECT id, label
                  FROM MyVideo JOIN LATERAL
                    UNNEST(DummyObjectDetector(data)) AS T(label)
                  WHERE id < 2 ORDER BY id;"""
        unnest_batch = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame(
                {
                    "myvideo.id": np.array([0, 1], dtype=np.intp),
                    "T.label": np.array(["person", "bicycle"]),
                }
            )
        )

        self.assertEqual(unnest_batch, expected)

        query = """SELECT id, label
                  FROM MyVideo JOIN LATERAL
                    UNNEST(DummyObjectDetector(data)) AS T
                  WHERE id < 2 ORDER BY id;"""
        unnest_batch = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame(
                {
                    "myvideo.id": np.array([0, 1], dtype=np.intp),
                    "T.label": np.array(["person", "bicycle"]),
                }
            )
        )

        self.assertEqual(unnest_batch, expected)

    @pytest.mark.torchtest
    def test_lateral_join_with_multiple_projects(self):
        select_query = """SELECT id, T.labels FROM DETRAC JOIN LATERAL
                        Yolo(data) AS T WHERE id < 5;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertTrue(all(actual_batch.frames.columns == ["detrac.id", "T.labels"]))
        self.assertEqual(len(actual_batch), 5)

    def test_should_select_star_in_table(self):
        select_query = "SELECT * FROM MyVideo;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT * FROM MyVideo WHERE id = 5;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected_batch = list(create_dummy_batches(filters=[5]))[0]
        self.assertEqual(actual_batch, expected_batch)
