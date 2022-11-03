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
import struct
import unittest
from unittest.mock import MagicMock

import mock
from mock import mock_open

from eva.catalog.column_type import ColumnType, NdArrayType
from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.configuration.configuration_manager import ConfigurationManager
from eva.storage.storage_engine import VideoStorageEngine


class VideoStorageEngineTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = None

    def create_sample_table(self):
        table_info = DataFrameMetadata("dataset", "dataset")
        column_1 = DataFrameColumn("id", ColumnType.INTEGER, False)
        column_2 = DataFrameColumn(
            "data", ColumnType.NDARRAY, False, NdArrayType.UINT8, [2, 2, 3]
        )
        table_info.schema = [column_1, column_2]
        return table_info

    def setUp(self):
        self.video_engine = VideoStorageEngine
        self.table = self.create_sample_table()
        self.curr_version = ConfigurationManager().get_value(
            "storage", "video_engine_version"
        )

    def tearDown(self):
        pass

    @mock.patch("pathlib.Path.mkdir")
    def test_should_raise_file_exist_error(self, m):
        m.side_effect = FileExistsError
        with self.assertRaises(FileExistsError):
            self.video_engine.create(self.table, if_not_exists=False)

    def test_invalid_metadata(self):
        corrupt_meta = struct.pack("!H", self.curr_version + 1)
        with mock.patch("builtins.open", mock_open(read_data=corrupt_meta)):
            with self.assertRaises(RuntimeError):
                list(self.video_engine._get_video_file_path("metadata"))

    def test_write(self):
        batch = MagicMock()
        batch.frames = []
        table = MagicMock()
        table.file_url = Exception()
        with self.assertRaises(Exception):
            self.video_engine.write(table, batch)
