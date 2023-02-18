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
from test.util import create_sample_csv, file_remove

import pandas as pd
from mock import MagicMock, patch

from eva.executor.executor_utils import ExecutorError
from eva.executor.load_executor import LoadDataExecutor
from eva.models.storage.batch import Batch
from eva.parser.table_ref import TableInfo
from eva.parser.types import FileFormatType


class LoadExecutorTest(unittest.TestCase):
    def _create_load_video_plan(self):
        file_path = "video"
        table_info = TableInfo("video")
        batch_mem_size = 3000
        file_options = {"file_format": FileFormatType.VIDEO}
        plan = type(
            "LoadDataPlan",
            (),
            {
                "table_info": table_info,
                "file_path": file_path,
                "batch_mem_size": batch_mem_size,
                "file_options": file_options,
            },
        )
        return plan

    @patch(
        "eva.catalog.catalog_manager.CatalogManager.get_table_catalog_entry",
        return_value=None,
    )
    def test_should_fail_to_find_table(self, catalog_mock):
        file_path = "dummy.csv"
        table_info = TableInfo("dummy")
        batch_mem_size = 3000
        file_options = {"file_format": FileFormatType.CSV}
        plan = type(
            "LoadDataPlan",
            (),
            {
                "table_info": table_info,
                "file_path": file_path,
                "batch_mem_size": batch_mem_size,
                "file_options": file_options,
            },
        )

        load_executor = LoadDataExecutor(plan)
        with self.assertRaises(ExecutorError):
            next(load_executor.exec())

    @patch("eva.catalog.catalog_manager.CatalogManager.get_table_catalog_entry")
    @patch("eva.executor.load_multimedia_executor.StorageEngine.factory")
    def test_should_call_csv_reader_and_storage_engine(
        self, factory_mock, catalog_mock
    ):
        # creates a dummy.csv
        create_sample_csv()

        file_path = "dummy.csv"
        table_info = TableInfo("dummy")
        batch_mem_size = 3000
        file_options = {}
        file_options["file_format"] = FileFormatType.CSV
        column_list = [
            type("ColumnCatalogEntry", (), {"name": "id"}),
            type("ColumnCatalogEntry", (), {"name": "frame_id"}),
            type("ColumnCatalogEntry", (), {"name": "video_id"}),
        ]
        table_obj = MagicMock(columns=column_list)
        catalog_mock.return_value = table_obj
        plan = type(
            "LoadDataPlan",
            (),
            {
                "table_info": table_info,
                "file_path": file_path,
                "batch_mem_size": batch_mem_size,
                "column_list": column_list,
                "file_options": file_options,
            },
        )

        load_executor = LoadDataExecutor(plan)
        batch = next(load_executor.exec())
        catalog_mock.assert_called_once_with("dummy", None)
        self.assertEqual(factory_mock.return_value.write.call_args.args[0], table_obj)

        # Note: We call exec() from the child classes.
        self.assertEqual(
            batch,
            Batch(pd.DataFrame([{"CSV": file_path, "Number of loaded frames": 20}])),
        )

        # remove the dummy.csv
        file_remove("dummy.csv")
