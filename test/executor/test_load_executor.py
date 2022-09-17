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
import unittest
from pathlib import Path
from test.util import create_sample_csv, file_remove

import pandas as pd
from mock import call, patch

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.load_executor import LoadDataExecutor
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.models.storage.batch import Batch
from eva.parser.types import FileFormatType


class LoadExecutorTest(unittest.TestCase):
    @patch("eva.executor.load_video_executor.VideoStorageEngine.create")
    @patch("eva.executor.load_video_executor.VideoStorageEngine.write")
    def test_should_call_opencv_reader_and_storage_engine(
        self, write_mock, create_mock
    ):
        file_path = "video"
        table_metainfo = "info"
        batch_mem_size = 3000
        file_options = {}
        file_options["file_format"] = FileFormatType.VIDEO
        plan = type(
            "LoadDataPlan",
            (),
            {
                "table_metainfo": table_metainfo,
                "file_path": file_path,
                "batch_mem_size": batch_mem_size,
                "file_options": file_options,
            },
        )

        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            batch = next(load_executor.exec())
            create_mock.assert_called_once_with(table_metainfo, if_not_exists=True)
            write_mock.assert_called_once_with(
                table_metainfo, Batch(pd.DataFrame([{"video_file_path": file_path}]))
            )
            expected = Batch(
                pd.DataFrame([{f"Video successfully added at location: {file_path}"}])
            )
            self.assertEqual(batch, expected)

    @patch("eva.executor.load_video_executor.VideoStorageEngine.create")
    @patch("eva.executor.load_video_executor.VideoStorageEngine.write")
    def test_should_search_in_upload_directory(self, write_mock, create_mock):
        self.upload_path = Path(
            ConfigurationManager().get_value("storage", "upload_dir")
        )
        file_path = "video"
        table_metainfo = "info"
        batch_mem_size = 3000
        file_options = {}
        file_options["file_format"] = FileFormatType.VIDEO
        plan = type(
            "LoadDataPlan",
            (),
            {
                "table_metainfo": table_metainfo,
                "file_path": file_path,
                "batch_mem_size": batch_mem_size,
                "file_options": file_options,
            },
        )

        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.side_effect = [False, True]
            batch = next(load_executor.exec())
            location = self.upload_path / file_path
            create_mock.assert_called_once_with(table_metainfo, if_not_exists=True)
            write_mock.assert_called_once_with(
                table_metainfo,
                Batch(pd.DataFrame([{"video_file_path": str(location)}])),
            )
            expected = Batch(
                pd.DataFrame([{f"Video successfully added at location: {location}"}])
            )
            self.assertEqual(batch, expected)

    @patch("eva.executor.load_video_executor.VideoStorageEngine.create")
    @patch("eva.executor.load_video_executor.VideoStorageEngine.write")
    def test_should_fail_to_find_file(self, write_mock, create_mock):
        file_path = "video"
        table_metainfo = "info"
        batch_mem_size = 3000
        file_options = {}
        file_options["file_format"] = FileFormatType.VIDEO
        column_list = None
        plan = type(
            "LoadDataPlan",
            (),
            {
                "table_metainfo": table_metainfo,
                "file_path": file_path,
                "batch_mem_size": batch_mem_size,
                "column_list": column_list,
                "file_options": file_options,
            },
        )

        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.side_effect = [False, False]
            with self.assertRaises(RuntimeError):
                next(load_executor.exec())

    @patch("eva.storage.storage_engine.StorageEngine.write")
    def test_should_call_csv_reader_and_storage_engine(self, write_mock):
        batch_frames = [list(range(5))] * 2

        # creates a dummy.csv
        create_sample_csv()

        file_path = "dummy.csv"
        table_metainfo = "info"
        batch_mem_size = 3000
        file_options = {}
        file_options["file_format"] = FileFormatType.CSV
        column_list = [
            TupleValueExpression(col_name="id", table_alias="dummy"),
            TupleValueExpression(col_name="frame_id", table_alias="dummy"),
            TupleValueExpression(col_name="video_id", table_alias="dummy"),
        ]
        plan = type(
            "LoadDataPlan",
            (),
            {
                "table_metainfo": table_metainfo,
                "file_path": file_path,
                "batch_mem_size": batch_mem_size,
                "column_list": column_list,
                "file_options": file_options,
            },
        )

        load_executor = LoadDataExecutor(plan)
        batch = next(load_executor.exec())
        write_mock.has_calls(
            call(table_metainfo, batch_frames[0]),
            call(table_metainfo, batch_frames[1]),
        )

        # Note: We call exec() from the child classes.
        self.assertEqual(
            batch,
            Batch(pd.DataFrame([{"CSV": file_path, "Number of loaded frames": 20}])),
        )

        # remove the dummy.csv
        file_remove("dummy.csv")
