# coding=utf-8
# Copyright 2018-2020 EVA
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
import pandas as pd
from pathlib import Path
from mock import patch
from eva.executor.load_executor import LoadDataExecutor
from eva.models.storage.batch import Batch
from eva.configuration.configuration_manager import ConfigurationManager


class LoadExecutorTest(unittest.TestCase):

    @patch('eva.executor.load_executor.VideoStorageEngine.create')
    def test_should_call_opencv_reader_and_storage_engine(
            self, create_mock):
        file_path = 'video'
        table_metainfo = 'info'
        batch_mem_size = 3000
        plan = type(
            "LoadDataPlan", (), {
                'file_path': file_path,
                'table_metainfo': table_metainfo,
                'batch_mem_size': batch_mem_size})

        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            batch = next(load_executor.exec())
            create_mock.assert_called_once_with(table_metainfo, file_path)
            self.assertEqual(batch, Batch(pd.DataFrame(
                [{'Video': file_path}])))

    @patch('eva.executor.load_executor.VideoStorageEngine.create')
    def test_should_search_in_upload_directory(
            self, create_mock):
        self.upload_path = Path(
            ConfigurationManager().get_value('storage', 'path_prefix'))
        file_path = 'video'
        table_metainfo = 'info'
        batch_mem_size = 3000
        plan = type(
            "LoadDataPlan", (), {
                'file_path': file_path,
                'table_metainfo': table_metainfo,
                'batch_mem_size': batch_mem_size})

        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.side_effect = [False, True]
            batch = next(load_executor.exec())
            create_mock.assert_called_once_with(
                table_metainfo, self.upload_path / file_path)
            self.assertEqual(batch, Batch(pd.DataFrame(
                [{'Video': file_path}])))

    @patch('eva.executor.load_executor.VideoStorageEngine.create')
    def test_should_fail_to_find_file(self, create_mock):
        file_path = 'video'
        table_metainfo = 'info'
        batch_mem_size = 3000
        plan = type(
            "LoadDataPlan", (), {
                'file_path': file_path,
                'table_metainfo': table_metainfo,
                'batch_mem_size': batch_mem_size})

        load_executor = LoadDataExecutor(plan)
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.side_effect = [False, False]
            with self.assertRaises(RuntimeError):
                next(load_executor.exec())
