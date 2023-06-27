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
import tempfile
import unittest
from test.util import (
    DummyObjectDetector,
    create_dummy_batches,
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from evadb.binder.binder_utils import BinderError
from evadb.catalog.catalog_type import ColumnType, NdArrayType
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


@pytest.mark.notparallel
class UDFExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        video_file_path = create_sample_video(NUM_FRAMES)
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(self.evadb, load_query)

        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

    def tearDown(self):
        shutdown_ray()
        file_remove("dummy.avi")
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideo;")

    # integration test

    def test_should_load_and_select_using_udf_video_in_table(self):
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        labels = DummyObjectDetector().labels
        expected = [
            {
                "myvideo.id": i,
                "dummyobjectdetector.label": np.array([labels[1 + i % 2]]),
            }
            for i in range(NUM_FRAMES)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_select_using_udf_video(self):
        # Equality test
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label = ['person'] ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected = [
            {
                "myvideo.id": i * 2,
                "dummyobjectdetector.label": np.array(["person"]),
            }
            for i in range(NUM_FRAMES // 2)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

        # Contain test
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label @> ['person'] ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(actual_batch, expected_batch)

        # Multi element contain test

        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label <@ ['person', 'bicycle'] \
            ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected = [
            {
                "myvideo.id": i * 2,
                "dummyobjectdetector.label": np.array(["person"]),
            }
            for i in range(NUM_FRAMES // 2)
        ]
        expected += [
            {
                "myvideo.id": i,
                "dummyobjectdetector.label": np.array(["bicycle"]),
            }
            for i in range(NUM_FRAMES)
            if i % 2 + 1 == 2
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        expected_batch.sort()

        self.assertEqual(actual_batch, expected_batch)
        nested_select_query = """SELECT name, id, data FROM
            (SELECT name, id, data, DummyObjectDetector(data) FROM MyVideo
                WHERE id >= 2
            ) AS T
            WHERE ['person'] <@ label;
            """
        actual_batch = execute_query_fetch_all(self.evadb, nested_select_query)
        actual_batch.sort()
        expected_batch = list(
            create_dummy_batches(
                filters=[i for i in range(2, NUM_FRAMES) if i % 2 == 0]
            )
        )[0]
        expected_batch = expected_batch.project(
            ["myvideo.name", "myvideo.id", "myvideo.data"]
        )
        expected_batch.modify_column_alias("T")
        self.assertEqual(actual_batch, expected_batch)

    def test_create_udf(self):
        udf_name = "DummyObjectDetector"
        create_udf_query = """CREATE UDF {}
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        # Try to create duplicate UDF
        with self.assertRaises(ExecutorError):
            actual = execute_query_fetch_all(
                self.evadb, create_udf_query.format(udf_name)
            )
            expected = Batch(pd.DataFrame([f"UDF {udf_name} already exists."]))
            self.assertEqual(actual, expected)

        # Try to create UDF if not exists
        actual = execute_query_fetch_all(
            self.evadb, create_udf_query.format("IF NOT EXISTS " + udf_name)
        )
        expected = Batch(
            pd.DataFrame([f"UDF {udf_name} already exists, nothing added."])
        )
        self.assertEqual(actual, expected)

    def test_should_create_udf_with_metadata(self):
        udf_name = "DummyObjectDetector"
        execute_query_fetch_all(self.evadb, f"DROP UDF {udf_name};")
        create_udf_query = """CREATE UDF {}
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py'
                  'CACHE' 'TRUE'
                  'BATCH' 'FALSE';
        """
        execute_query_fetch_all(self.evadb, create_udf_query.format(udf_name))

        # try fetching the metadata values
        entries = self.evadb.catalog().get_udf_metadata_entries_by_udf_name(udf_name)
        self.assertEqual(len(entries), 2)
        metadata = [(entry.key, entry.value) for entry in entries]

        expected_metadata = [("CACHE", "TRUE"), ("BATCH", "FALSE")]
        self.assertEqual(set(metadata), set(expected_metadata))

    def test_should_return_empty_metadata_list_for_missing_udf(self):
        # missing udf should return empty list
        entries = self.evadb.catalog().get_udf_metadata_entries_by_udf_name("randomUDF")
        self.assertEqual(len(entries), 0)

    def test_should_return_empty_metadata_list_if_udf_is_removed(self):
        udf_name = "DummyObjectDetector"
        execute_query_fetch_all(self.evadb, f"DROP UDF {udf_name};")
        create_udf_query = """CREATE UDF {}
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py'
                  'CACHE' 'TRUE'
                  'BATCH' 'FALSE';
        """
        execute_query_fetch_all(self.evadb, create_udf_query.format(udf_name))

        # try fetching the metadata values
        entries = self.evadb.catalog().get_udf_metadata_entries_by_udf_name(udf_name)
        self.assertEqual(len(entries), 2)

        # remove the udf
        execute_query_fetch_all(self.evadb, f"DROP UDF {udf_name};")
        # try fetching the metadata values
        entries = self.evadb.catalog().get_udf_metadata_entries_by_udf_name(udf_name)
        self.assertEqual(len(entries), 0)

    def test_should_raise_using_missing_udf(self):
        select_query = "SELECT id,DummyObjectDetector1(data) FROM MyVideo \
            ORDER BY id;"
        with self.assertRaises(BinderError) as cm:
            execute_query_fetch_all(
                self.evadb, select_query, do_not_print_exceptions=True
            )

        err_msg = (
            "Function 'DummyObjectDetector1' does not exist in the catalog. "
            "Please create the function using CREATE UDF command."
        )
        self.assertEqual(str(cm.exception), err_msg)

    def test_should_raise_for_udf_name_mismatch(self):
        create_udf_query = """CREATE UDF TestUDF
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(
                self.evadb, create_udf_query, do_not_print_exceptions=True
            )

    def test_should_raise_if_udf_file_is_modified(self):
        execute_query_fetch_all(self.evadb, "DROP UDF DummyObjectDetector;")

        # Test IF EXISTS
        execute_query_fetch_all(self.evadb, "DROP UDF IF EXISTS DummyObjectDetector;")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as tmp_file:
            with open("test/util.py", "r") as file:
                tmp_file.write(file.read())

            tmp_file.seek(0)

            udf_name = "DummyObjectDetector"
            create_udf_query = """CREATE UDF {}
                    INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                    OUTPUT (label NDARRAY STR(10))
                    TYPE  Classification
                    IMPL  '{}';
            """
            execute_query_fetch_all(
                self.evadb, create_udf_query.format(udf_name, tmp_file.name)
            )

            # Modify the udf file by appending
            tmp_file.seek(0, 2)
            tmp_file.write("#comment")
            tmp_file.seek(0)

            select_query = (
                "SELECT id,DummyObjectDetector(data) FROM MyVideo ORDER BY id;"
            )

            # disabling warning for UDF modificiation for now
            # with self.assertRaises(AssertionError):
            execute_query_fetch_all(self.evadb, select_query)

    def test_create_udf_with_decorators(self):
        execute_query_fetch_all(
            self.evadb, "DROP UDF IF EXISTS DummyObjectDetectorDecorators;"
        )
        create_udf_query = """CREATE UDF DummyObjectDetectorDecorators
                  IMPL  'test/util.py';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        catalog_manager = self.evadb.catalog()
        udf_obj = catalog_manager.get_udf_catalog_entry_by_name(
            "DummyObjectDetectorDecorators"
        )
        udf_inputs = catalog_manager.get_udf_io_catalog_input_entries(udf_obj)
        self.assertEquals(len(udf_inputs), 1)

        udf_input = udf_inputs[0]

        expected_input_attributes = {
            "name": "Frame_Array",
            "type": ColumnType.NDARRAY,
            "is_nullable": False,
            "array_type": NdArrayType.UINT8,
            "array_dimensions": (3, 256, 256),
            "is_input": True,
        }

        for attr in expected_input_attributes:
            self.assertEquals(getattr(udf_input, attr), expected_input_attributes[attr])

        udf_outputs = catalog_manager.get_udf_io_catalog_output_entries(udf_obj)
        self.assertEquals(len(udf_outputs), 1)

        udf_output = udf_outputs[0]
        expected_output_attributes = {
            "name": "label",
            "type": ColumnType.NDARRAY,
            "is_nullable": False,
            "array_type": NdArrayType.STR,
            "array_dimensions": (),
            "is_input": False,
        }

        for attr in expected_output_attributes:
            self.assertEquals(
                getattr(udf_output, attr), expected_output_attributes[attr]
            )

    def test_udf_cost_entry_created(self):
        execute_query_fetch_all(
            self.evadb, "SELECT DummyObjectDetector(data) FROM MyVideo"
        )
        entry = self.evadb.catalog().get_udf_cost_catalog_entry("DummyObjectDetector")
        self.assertIsNotNone(entry)
