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
import glob
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from test.util import (
    create_dummy_batches,
    create_dummy_csv_batches,
    create_sample_csv,
    create_sample_video,
    file_remove,
)

import numpy as np
import pandas as pd

from eva.binder.binder_utils import BinderError
from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.models.storage.batch import Batch
from eva.parser.types import FileFormatType
from eva.server.command_handler import execute_query_fetch_all


class LoadExecutorTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        self.video_file_path = create_sample_video()
        self.image_files_path = Path(
            f"{EVA_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/*.jpg"
        )
        create_sample_csv()

    def tearDown(self):
        file_remove("dummy.avi")
        file_remove("dummy.csv")
        # clean up
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideos;")

    # integration test for load video
    def test_should_load_video_in_table(self):
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(query)

        select_query = """SELECT * FROM MyVideo;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        self.assertEqual(actual_batch, expected_batch)
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    def test_should_load_videos_in_table(self):
        path = f"{EVA_ROOT_DIR}/data/sample_videos/1/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        result = execute_query_fetch_all(query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.VIDEO.name}: 2"])
        )
        self.assertEqual(result, expected)

    def test_should_load_videos_with_same_name_but_different_path(self):
        path = f"{EVA_ROOT_DIR}/data/sample_videos/**/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        result = execute_query_fetch_all(query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.VIDEO.name}: 3"])
        )
        self.assertEqual(result, expected)

    def test_should_fail_to_load_videos_with_same_path(self):
        path = f"{EVA_ROOT_DIR}/data/sample_videos/2/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        result = execute_query_fetch_all(query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.VIDEO.name}: 1"])
        )
        self.assertEqual(result, expected)

        # original file should be preserved
        expected_output = execute_query_fetch_all("SELECT id FROM MyVideos;")

        # try adding duplicate files to the table
        path = f"{EVA_ROOT_DIR}/data/sample_videos/**/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(query)

        # original data should be preserved
        after_load_fail = execute_query_fetch_all("SELECT id FROM MyVideos;")

        self.assertEqual(expected_output, after_load_fail)

    def test_should_fail_to_load_corrupt_video(self):
        # should fail on an empty file
        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as tmp:
            query = f"""LOAD VIDEO "{tmp.name}" INTO MyVideos;"""
            with self.assertRaises(Exception):
                execute_query_fetch_all(query)

    def test_should_fail_to_load_invalid_files_as_video(self):
        path = f"{EVA_ROOT_DIR}/data/**"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(query)
        with self.assertRaises(BinderError):
            execute_query_fetch_all("SELECT name FROM MyVideos")

    def test_should_rollback_if_video_load_fails(self):
        path_regex = Path(f"{EVA_ROOT_DIR}/data/sample_videos/1/*.mp4")
        valid_videos = glob.glob(str(path_regex.expanduser()), recursive=True)

        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as empty_file:
            # Load one correct file and one empty file
            # nothing should be added
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_videos[0]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(query)
                with self.assertRaises(BinderError):
                    execute_query_fetch_all("SELECT name FROM MyVideos")

            # Load two correct file and one empty file
            # nothing should be added
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_videos[0]), tmp_dir)
                shutil.copy2(str(valid_videos[1]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(query)
                with self.assertRaises(BinderError):
                    execute_query_fetch_all("SELECT name FROM MyVideos")

    def test_should_rollback_and_preserve_previous_state(self):
        path_regex = Path(f"{EVA_ROOT_DIR}/data/sample_videos/1/*.mp4")
        valid_videos = glob.glob(str(path_regex.expanduser()), recursive=True)
        # Load one correct file
        # commit
        load_file = f"{EVA_ROOT_DIR}/data/sample_videos/1/1.mp4"
        execute_query_fetch_all(f"""LOAD VIDEO "{load_file}" INTO MyVideos;""")

        # Load one correct file and one empty file
        # original file should remain
        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as empty_file:
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_videos[1]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(query)
                result = execute_query_fetch_all("SELECT name FROM MyVideos")
                file_names = np.unique(result.frames)
                self.assertEqual(len(file_names), 1)

    ###########################################
    # integration testcases for load image
    def test_should_load_images_in_table(self):
        num_files = len(
            glob.glob(os.path.expanduser(self.image_files_path), recursive=True)
        )
        query = f"""LOAD IMAGE "{self.image_files_path}" INTO MyImages;"""
        result = execute_query_fetch_all(query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.IMAGE.name}: {num_files}"])
        )
        self.assertEqual(result, expected)

    def test_should_fail_to_load_images_with_same_path(self):
        image_files = glob.glob(
            os.path.expanduser(self.image_files_path), recursive=True
        )
        query = f"""LOAD IMAGE "{image_files[0]}" INTO MyImages;"""
        result = execute_query_fetch_all(query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.IMAGE.name}: 1"])
        )
        self.assertEqual(result, expected)

        # original file should be preserved
        expected_output = execute_query_fetch_all("SELECT name FROM MyImages;")

        # try adding duplicate files to the table
        query = f"""LOAD IMAGE "{image_files[0]}" INTO MyImages;"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(query)

        # original data should be preserved
        after_load_fail = execute_query_fetch_all("SELECT name FROM MyImages;")

        self.assertEqual(expected_output, after_load_fail)

    def test_should_fail_to_load_corrupt_image(self):
        # should fail on an empty file
        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as tmp:
            query = f"""LOAD IMAGE "{tmp.name}" INTO MyImages;"""
            with self.assertRaises(Exception):
                execute_query_fetch_all(query)

    def test_should_fail_to_load_invalid_files_as_image(self):
        path = f"{EVA_ROOT_DIR}/data/**"
        query = f"""LOAD IMAGE "{path}" INTO MyImages;"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(query)
        with self.assertRaises(BinderError):
            execute_query_fetch_all("SELECT name FROM MyImages;")

    def test_should_rollback_if_image_load_fails(self):
        valid_images = glob.glob(
            str(self.image_files_path.expanduser()), recursive=True
        )

        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as empty_file:
            # Load one correct file and one empty file
            # nothing should be added
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_images[0]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD IMAGE "{path}" INTO MyImages;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(query)
                with self.assertRaises(BinderError):
                    execute_query_fetch_all("SELECT name FROM MyImages;")

            # Load two correct file and one empty file
            # nothing should be added
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_images[0]), tmp_dir)
                shutil.copy2(str(valid_images[1]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD IMAGE "{path}" INTO MyImages;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(query)
                with self.assertRaises(BinderError):
                    execute_query_fetch_all("SELECT name FROM MyImages;")

    def test_should_rollback_and_preserve_previous_state_for_load_images(self):
        valid_images = glob.glob(
            str(self.image_files_path.expanduser()), recursive=True
        )
        # Load one correct file
        # commit
        execute_query_fetch_all(f"""LOAD IMAGE "{valid_images[0]}" INTO MyImages;""")

        # Load one correct file and one empty file
        # original file should remain
        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as empty_file:
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_images[1]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD IMAGE "{path}" INTO MyImages;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(query)
                result = execute_query_fetch_all("SELECT name FROM MyImages")
                self.assertEqual(len(result), 1)
                expected = Batch(pd.DataFrame([{"myimages.name": valid_images[0]}]))
                self.assertEqual(expected, result)

    ###################################
    # integration tests for csv
    def test_should_load_csv_in_table(self):

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

        # execute a select query
        select_query = """SELECT id, frame_id, video_id,
                          dataset_name, label, bbox,
                          object_id
                          FROM MyVideoCSV;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()

        # assert the batches are equal
        expected_batch = create_dummy_csv_batches()
        expected_batch.modify_column_alias("myvideocsv")
        self.assertEqual(actual_batch, expected_batch)

        # clean up
        drop_query = "DROP TABLE IF EXISTS MyVideoCSV;"
        execute_query_fetch_all(drop_query)

    def test_should_load_csv_with_columns_in_table(self):

        # loading a csv requires a table to be created first
        create_table_query = """

            CREATE TABLE IF NOT EXISTS MyVideoCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL,
                dataset_name TEXT(30) NOT NULL
            );
            """
        execute_query_fetch_all(create_table_query)

        # load the CSV
        load_query = """LOAD CSV 'dummy.csv' INTO MyVideoCSV (id, frame_id, video_id, dataset_name);"""
        execute_query_fetch_all(load_query)

        # execute a select query
        select_query = """SELECT id, frame_id, video_id, dataset_name
                          FROM MyVideoCSV;"""

        actual_batch = execute_query_fetch_all(select_query)
        actual_batch.sort()

        # assert the batches are equal
        select_columns = ["id", "frame_id", "video_id", "dataset_name"]
        expected_batch = create_dummy_csv_batches(target_columns=select_columns)
        expected_batch.modify_column_alias("myvideocsv")
        self.assertEqual(actual_batch, expected_batch)

        # clean up
        drop_query = "DROP TABLE IF EXISTS MyVideoCSV;"
        execute_query_fetch_all(drop_query)


if __name__ == "__main__":
    unittest.main()
