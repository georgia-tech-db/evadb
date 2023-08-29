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
import glob
import multiprocessing as mp
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from test.util import (
    create_dummy_batches,
    create_dummy_csv_batches,
    create_large_scale_image_dataset,
    create_sample_csv,
    create_sample_video,
    file_remove,
    get_evadb_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from evadb.binder.binder_utils import BinderError
from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.parser.types import FileFormatType
from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class LoadExecutorTests(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()
        self.video_file_path = create_sample_video()
        self.image_files_path = Path(
            f"{EvaDB_ROOT_DIR}/test/data/uadetrac/small-data/MVI_20011/*.jpg"
        )
        self.csv_file_path = create_sample_csv()

    def tearDown(self):
        shutdown_ray()

        file_remove("dummy.avi")
        file_remove("dummy.csv")
        # clean up
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideos;")

    # integration test for load video
    def test_should_load_video_in_table(self):
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(self.evadb, query)

        select_query = """SELECT * FROM MyVideo;"""

        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        self.assertEqual(actual_batch, expected_batch)
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideo;")

    def test_should_form_symlink_to_individual_video(self):
        catalog_manager = self.evadb.catalog()
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(self.evadb, query)

        table_catalog_entry = catalog_manager.get_table_catalog_entry("MyVideo")
        video_dir = table_catalog_entry.file_url

        # the video directory would have only a single file
        self.assertEqual(len(os.listdir(video_dir)), 1)
        video_file = os.listdir(video_dir)[0]
        # check that the file is a symlink to self.video_file_path
        video_file_path = os.path.join(video_dir, video_file)
        self.assertTrue(os.path.islink(video_file_path))
        self.assertEqual(os.readlink(video_file_path), self.video_file_path)

        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyVideo;")

    def test_should_raise_error_on_removing_symlinked_file(self):
        query = f"LOAD VIDEO '{self.video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(self.evadb, query)

        select_query = """SELECT * FROM MyVideo;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        self.assertEqual(actual_batch, expected_batch)

        # remove the source file
        file_remove("dummy.avi")

        # try to read the table again
        with self.assertRaises(ExecutorError) as e:
            execute_query_fetch_all(
                self.evadb, select_query, do_not_print_exceptions=True
            )
        self.assertEqual(
            str(e.exception),
            "The dataset file could not be found. Please verify that the file exists in the specified path.",
        )

        # create the file again for other test cases
        create_sample_video()

    def test_should_form_symlink_to_multiple_videos(self):
        catalog_manager = self.evadb.catalog()
        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/1/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        execute_query_fetch_all(self.evadb, query)

        table_catalog_entry = catalog_manager.get_table_catalog_entry("MyVideos")
        video_dir = table_catalog_entry.file_url

        # the video directory would have two files
        self.assertEqual(len(os.listdir(video_dir)), 2)
        video_files = os.listdir(video_dir)
        # check that the files are symlinks to the original videos
        for video_file in video_files:
            video_file_path = os.path.join(video_dir, video_file)
            self.assertTrue(os.path.islink(video_file_path))
            self.assertTrue(
                os.readlink(video_file_path).startswith(
                    f"{EvaDB_ROOT_DIR}/data/sample_videos/1"
                )
            )

    def test_should_load_videos_with_same_name_but_different_path(self):
        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/**/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        result = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.VIDEO.name}: 4"])
        )
        self.assertEqual(result, expected)

    def test_should_fail_to_load_videos_with_same_path(self):
        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/2/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        result = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.VIDEO.name}: 1"])
        )
        self.assertEqual(result, expected)

        # original file should be preserved
        expected_output = execute_query_fetch_all(
            self.evadb, "SELECT id FROM MyVideos;"
        )

        # try adding duplicate files to the table
        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/**/*.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)

        # original data should be preserved
        after_load_fail = execute_query_fetch_all(
            self.evadb, "SELECT id FROM MyVideos;"
        )

        self.assertEqual(expected_output, after_load_fail)

    def test_should_fail_to_load_missing_video(self):
        path = f"{EvaDB_ROOT_DIR}/data/sample_videos/missing.mp4"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        with self.assertRaises(ExecutorError) as exc_info:
            execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)
        self.assertIn(
            "Load VIDEO failed",
            str(exc_info.exception),
        )

    def test_should_fail_to_load_corrupt_video(self):
        # should fail on an empty file
        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as tmp:
            query = f"""LOAD VIDEO "{tmp.name}" INTO MyVideos;"""
            with self.assertRaises(Exception):
                execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)

    def test_should_fail_to_load_invalid_files_as_video(self):
        path = f"{EvaDB_ROOT_DIR}/data/README.md"
        query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)
        with self.assertRaises(BinderError):
            execute_query_fetch_all(
                self.evadb, "SELECT name FROM MyVideos", do_not_print_exceptions=True
            )

    def test_should_rollback_if_video_load_fails(self):
        path_regex = Path(f"{EvaDB_ROOT_DIR}/data/sample_videos/1/*.mp4")
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
                    execute_query_fetch_all(
                        self.evadb, query, do_not_print_exceptions=True
                    )
                with self.assertRaises(BinderError):
                    execute_query_fetch_all(
                        self.evadb,
                        "SELECT name FROM MyVideos",
                        do_not_print_exceptions=True,
                    )

            # Load two correct file and one empty file
            # nothing should be added
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_videos[0]), tmp_dir)
                shutil.copy2(str(valid_videos[1]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD VIDEO "{path}" INTO MyVideos;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(
                        self.evadb, query, do_not_print_exceptions=True
                    )
                with self.assertRaises(BinderError):
                    execute_query_fetch_all(
                        self.evadb,
                        "SELECT name FROM MyVideos",
                        do_not_print_exceptions=True,
                    )

    def test_should_rollback_and_preserve_previous_state(self):
        path_regex = Path(f"{EvaDB_ROOT_DIR}/data/sample_videos/1/*.mp4")
        valid_videos = glob.glob(str(path_regex.expanduser()), recursive=True)
        # Load one correct file
        # commit
        load_file = f"{EvaDB_ROOT_DIR}/data/sample_videos/1/1.mp4"
        execute_query_fetch_all(
            self.evadb, f"""LOAD VIDEO "{load_file}" INTO MyVideos;"""
        )

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
                    execute_query_fetch_all(
                        self.evadb, query, do_not_print_exceptions=True
                    )
                result = execute_query_fetch_all(
                    self.evadb, "SELECT name FROM MyVideos"
                )
                file_names = np.unique(result.frames)
                self.assertEqual(len(file_names), 1)

    ###########################################
    # integration testcases for load image

    def test_should_fail_to_load_missing_image(self):
        path = f"{EvaDB_ROOT_DIR}/data/sample_images/missing.jpg"
        query = f"""LOAD IMAGE "{path}" INTO MyImages;"""
        with self.assertRaises(ExecutorError) as exc_info:
            execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)
        self.assertIn(
            "Load IMAGE failed",
            str(exc_info.exception),
        )

    def test_should_fail_to_load_images_with_same_path(self):
        image_files = glob.glob(
            os.path.expanduser(self.image_files_path), recursive=True
        )
        query = f"""LOAD IMAGE "{image_files[0]}" INTO MyImages;"""
        result = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame([f"Number of loaded {FileFormatType.IMAGE.name}: 1"])
        )
        self.assertEqual(result, expected)

        # original file should be preserved
        expected_output = execute_query_fetch_all(
            self.evadb, "SELECT name FROM MyImages;"
        )

        # try adding duplicate files to the table
        query = f"""LOAD IMAGE "{image_files[0]}" INTO MyImages;"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)

        # original data should be preserved
        after_load_fail = execute_query_fetch_all(
            self.evadb, "SELECT name FROM MyImages;"
        )

        self.assertEqual(expected_output, after_load_fail)

    def test_should_fail_to_load_corrupt_image(self):
        # should fail on an empty file
        tempfile_name = os.urandom(24).hex()
        tempfile_path = os.path.join(tempfile.gettempdir(), tempfile_name)
        with open(tempfile_path, "wb") as tmp:
            query = f"""LOAD IMAGE "{tmp.name}" INTO MyImages;"""
            with self.assertRaises(Exception):
                execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)

    def test_should_fail_to_load_invalid_files_as_image(self):
        path = f"{EvaDB_ROOT_DIR}/data/README.md"
        query = f"""LOAD IMAGE "{path}" INTO MyImages;"""
        with self.assertRaises(Exception):
            execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)
        with self.assertRaises(BinderError):
            execute_query_fetch_all(
                self.evadb, "SELECT name FROM MyImages;", do_not_print_exceptions=True
            )

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
                    execute_query_fetch_all(
                        self.evadb, query, do_not_print_exceptions=True
                    )
                with self.assertRaises(BinderError):
                    execute_query_fetch_all(
                        self.evadb,
                        "SELECT name FROM MyImages;",
                        do_not_print_exceptions=True,
                    )

            # Load two correct file and one empty file
            # nothing should be added
            with tempfile.TemporaryDirectory() as tmp_dir:
                shutil.copy2(str(valid_images[0]), tmp_dir)
                shutil.copy2(str(valid_images[1]), tmp_dir)
                shutil.copy2(str(empty_file.name), tmp_dir)
                path = Path(tmp_dir) / "*"
                query = f"""LOAD IMAGE "{path}" INTO MyImages;"""
                with self.assertRaises(Exception):
                    execute_query_fetch_all(
                        self.evadb, query, do_not_print_exceptions=True
                    )
                with self.assertRaises(BinderError):
                    execute_query_fetch_all(
                        self.evadb,
                        "SELECT name FROM MyImages;",
                        do_not_print_exceptions=True,
                    )

    def test_should_rollback_and_preserve_previous_state_for_load_images(self):
        valid_images = glob.glob(
            str(self.image_files_path.expanduser()), recursive=True
        )
        # Load one correct file
        # commit
        execute_query_fetch_all(
            self.evadb, f"""LOAD IMAGE "{valid_images[0]}" INTO MyImages;"""
        )

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
                    execute_query_fetch_all(
                        self.evadb, query, do_not_print_exceptions=True
                    )
                result = execute_query_fetch_all(
                    self.evadb, "SELECT name FROM MyImages"
                )
                self.assertEqual(len(result), 1)
                expected = Batch(pd.DataFrame([{"myimages.name": valid_images[0]}]))
                self.assertEqual(expected, result)

    ###################################
    # integration tests for csv
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
        execute_query_fetch_all(self.evadb, create_table_query)

        # load the CSV
        load_query = """LOAD CSV '{}' INTO MyVideoCSV (id, frame_id, video_id, dataset_name);""".format(
            self.csv_file_path
        )
        execute_query_fetch_all(self.evadb, load_query)

        # execute a select query
        select_query = """SELECT id, frame_id, video_id, dataset_name
                          FROM MyVideoCSV;"""

        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()

        # assert the batches are equal
        select_columns = ["id", "frame_id", "video_id", "dataset_name"]
        expected_batch = next(create_dummy_csv_batches(target_columns=select_columns))
        expected_batch.modify_column_alias("myvideocsv")
        self.assertEqual(actual_batch, expected_batch)

        # clean up
        drop_query = "DROP TABLE IF EXISTS MyVideoCSV;"
        execute_query_fetch_all(self.evadb, drop_query)

    def test_should_use_parallel_load(self):
        # Create images.
        large_scale_image_files_path = create_large_scale_image_dataset(
            mp.cpu_count() * 10
        )

        load_query = f"LOAD IMAGE '{large_scale_image_files_path}/**/*.jpg' INTO MyLargeScaleImages;"
        execute_query_fetch_all(self.evadb, load_query)

        drop_query = "DROP TABLE IF EXISTS MyLargeScaleImages;"
        execute_query_fetch_all(self.evadb, drop_query)

        # Clean up large scale image directory.
        shutil.rmtree(large_scale_image_files_path)

    def test_parallel_load_should_raise_exception(self):
        # Create images.
        large_scale_image_files_path = create_large_scale_image_dataset(
            mp.cpu_count() * 10
        )

        # Corrupt an image.
        with open(os.path.join(large_scale_image_files_path, "img0.jpg"), "w") as f:
            f.write("aa")

        with self.assertRaises(ExecutorError):
            load_query = f"LOAD IMAGE '{large_scale_image_files_path}/**/*.jpg' INTO MyLargeScaleImages;"
            execute_query_fetch_all(
                self.evadb, load_query, do_not_print_exceptions=True
            )

        drop_query = "DROP TABLE IF EXISTS MyLargeScaleImages;"
        execute_query_fetch_all(self.evadb, drop_query)

        # Clean up large scale image directory.
        shutil.rmtree(large_scale_image_files_path)

    def test_load_pdfs(self):
        execute_query_fetch_all(
            self.evadb,
            f"""LOAD DOCUMENT '{EvaDB_ROOT_DIR}/data/documents/*.pdf' INTO pdfs;""",
        )
        result = execute_query_fetch_all(self.evadb, "SELECT * from pdfs;")
        self.assertEqual(len(result.columns), 4)
        self.assertEqual(len(result), 26)


if __name__ == "__main__":
    unittest.main()
