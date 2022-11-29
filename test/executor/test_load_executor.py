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
from mock import MagicMock, call, patch

from eva.configuration.configuration_manager import ConfigurationManager
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

    @patch("eva.catalog.catalog_manager.CatalogManager.create_video_metadata")
    @patch(
        "eva.catalog.catalog_manager.CatalogManager.get_dataset_metadata",
        return_value=None,
    )
    @patch("eva.executor.load_video_executor.StorageEngine.factory")
    def test_should_call_opencv_reader_and_storage_engine(
        self, factory_mock, get_mock, create_mock
    ):
        table_obj = MagicMock()
        create_mock.return_value = table_obj

        plan = self._create_load_video_plan()
        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            batch = next(load_executor.exec())
            factory_mock.return_value.create.assert_called_once_with(table_obj)
            factory_mock.return_value.write.assert_called_once_with(
                table_obj, Batch(pd.DataFrame([{"video_file_path": plan.file_path}]))
            )
            expected = Batch(
                pd.DataFrame(
                    [{f"Video successfully added at location: {plan.file_path}"}]
                )
            )
            self.assertEqual(batch, expected)

    @patch("eva.catalog.catalog_manager.CatalogManager.create_video_metadata")
    @patch(
        "eva.catalog.catalog_manager.CatalogManager.get_dataset_metadata",
        return_value=None,
    )
    @patch("eva.executor.load_video_executor.StorageEngine.factory")
    def test_should_search_in_upload_directory(
        self, factory_mock, catalog_mock, create_mock
    ):
        table_obj = MagicMock()
        create_mock.return_value = table_obj
        plan = self._create_load_video_plan()
        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.side_effect = [False, True]
            batch = next(load_executor.exec())
            upload_path = Path(
                ConfigurationManager().get_value("storage", "upload_dir")
            )
            location = upload_path / plan.file_path
            factory_mock.return_value.create.assert_called_once_with(table_obj)
            factory_mock.return_value.write.assert_called_once_with(
                table_obj,
                Batch(pd.DataFrame([{"video_file_path": str(location)}])),
            )
            expected = Batch(
                pd.DataFrame([{f"Video successfully added at location: {location}"}])
            )
            self.assertEqual(batch, expected)

    @patch("eva.executor.load_video_executor.StorageEngine.factory")
    def test_should_fail_to_find_file(self, factory_mock):
        load_executor = LoadDataExecutor(self._create_load_video_plan())
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.side_effect = [False, False]
            with self.assertRaises(RuntimeError):
                next(load_executor.exec())

    @patch("eva.catalog.catalog_manager.CatalogManager.get_dataset_metadata")
    @patch("eva.executor.load_video_executor.StorageEngine.factory")
    def test_should_call_csv_reader_and_storage_engine(
        self, factory_mock, catalog_mock
    ):
        batch_frames = [list(range(5))] * 2

        # creates a dummy.csv
        create_sample_csv()

        file_path = "dummy.csv"
        table_info = TableInfo("dummy")
        batch_mem_size = 3000
        file_options = {}
        file_options["file_format"] = FileFormatType.CSV
        column_list = [
            type("DataFrameColumn", (), {"name": "id"}),
            type("DataFrameColumn", (), {"name": "frame_id"}),
            type("DataFrameColumn", (), {"name": "video_id"}),
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
        catalog_mock.assert_called_once_with(None, "dummy")
        factory_mock.return_value.write.has_calls(
            call(table_obj, batch_frames[0]),
            call(table_obj, batch_frames[1]),
        )

        # Note: We call exec() from the child classes.
        self.assertEqual(
            batch,
            Batch(pd.DataFrame([{"CSV": file_path, "Number of loaded frames": 20}])),
        )

        # remove the dummy.csv
        file_remove("dummy.csv")
