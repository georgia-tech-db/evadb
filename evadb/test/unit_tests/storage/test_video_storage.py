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
from test.util import (
    create_sample_video,
    get_evadb_for_testing,
    suffix_pytest_xdist_worker_id_to_dir,
)
from unittest.mock import MagicMock

import mock
import pandas as pd
import pytest

from evadb.catalog.catalog_type import ColumnType, NdArrayType, TableType
from evadb.catalog.models.column_catalog import ColumnCatalogEntry
from evadb.catalog.models.table_catalog import TableCatalogEntry
from evadb.models.storage.batch import Batch
from evadb.storage.storage_engine import StorageEngine


@pytest.mark.notparallel
class VideoStorageEngineTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = None

    def create_sample_table(self):
        table_info = TableCatalogEntry(
            str(suffix_pytest_xdist_worker_id_to_dir("dataset")),
            str(suffix_pytest_xdist_worker_id_to_dir("dataset")),
            table_type=TableType.VIDEO_DATA,
        )
        column_1 = ColumnCatalogEntry("id", ColumnType.INTEGER, False)
        column_2 = ColumnCatalogEntry(
            "data", ColumnType.NDARRAY, False, NdArrayType.UINT8, [2, 2, 3]
        )
        table_info.schema = [column_1, column_2]
        return table_info

    def setUp(self):
        evadb = get_evadb_for_testing()
        mock.table_type = TableType.VIDEO_DATA
        self.video_engine = StorageEngine.factory(evadb, mock)
        self.table = self.create_sample_table()

    def tearDown(self):
        pass

    @mock.patch("pathlib.Path.mkdir")
    def test_should_raise_file_exist_error(self, m):
        m.side_effect = FileExistsError
        with self.assertRaises(FileExistsError):
            self.video_engine.create(self.table, if_not_exists=False)
        self.video_engine.create(self.table, if_not_exists=True)

    def test_write(self):
        batch = MagicMock()
        batch.frames = []
        table = MagicMock()
        table.file_url = Exception()
        with self.assertRaises(Exception):
            self.video_engine.write(table, batch)

    def test_delete(self):
        batch = MagicMock()
        batch.frames = []
        table = MagicMock()
        table.file_url = Exception()
        with self.assertRaises(Exception):
            self.video_engine.delete(table, batch)

        self.video_engine.create(self.table, if_not_exists=True)
        video_file_path = create_sample_video()
        df = pd.DataFrame([video_file_path], columns=["file_path"])
        batch = Batch(df)

        # missing file
        with self.assertRaises(Exception):
            self.video_engine.delete(self.table, batch)

        self.video_engine.drop(self.table)

    def test_rename(self):
        table_info = TableCatalogEntry(
            "new_name", "new_name", table_type=TableType.VIDEO_DATA
        )

        with pytest.raises(Exception):
            self.video_engine.rename(self.table, table_info)

    def test_media_storage_engine_exceptions(self):
        missing_table_info = TableCatalogEntry(
            "missing_table", None, table_type=TableType.VIDEO_DATA
        )

        with self.assertRaises(Exception):
            self.video_engine.drop(missing_table_info)

        with self.assertRaises(Exception):
            self.video_engine.write(missing_table_info, None)

        with self.assertRaises(Exception):
            read_batch = list(self.video_engine.read(missing_table_info))
            self.assertEqual(read_batch, None)

        with self.assertRaises(Exception):
            self.video_engine.delete(missing_table_info, None)
