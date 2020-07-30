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
from mock import patch, MagicMock, call
from src.executor.load_executor import LoadDataExecutor


class LoadExecutorTest(unittest.TestCase):
    @patch('src.executor.load_executor.OpenCVReader')
    @patch('src.executor.load_executor.append_rows')
    @patch('src.executor.load_executor.ConfigurationManager.get_value')
    def test_should_call_opencv_reader_and_storage_engine_and_config(
            self, get_val_mock, append_mock, cv_mock):
        batch_frames = [list(range(5))] * 2
        attrs = {'read.return_value': batch_frames}
        cv_mock.return_value = MagicMock(**attrs)
        get_val_mock.return_value = 40
        file_path = 'video'
        table_metainfo = 'info'
        plan = type(
            "LoadDataPlan", (), {
                'file_path': file_path, 'table_metainfo': table_metainfo})

        load_executor = LoadDataExecutor(plan)
        load_executor.exec()
        get_val_mock.assert_called_once_with("executor", "batch_size")
        cv_mock.assert_called_once_with(file_path, batch_size=40)
        append_mock.has_calls(call(table_metainfo, batch_frames[0]), call(
            table_metainfo, batch_frames[0]))

    @patch('src.executor.load_executor.OpenCVReader')
    @patch('src.executor.load_executor.append_rows')
    @patch('src.executor.load_executor.ConfigurationManager.get_value')
    def test_exec_config_returns_None(
            self, get_val_mock, append_mock, cv_mock):
        batch_frames = [list(range(5))] * 2
        attrs = {'read.return_value': batch_frames}
        cv_mock.return_value = MagicMock(**attrs)
        get_val_mock.return_value = None
        file_path = 'video'
        table_metainfo = 'info'
        plan = type(
            "LoadDataPlan", (), {
                'file_path': file_path, 'table_metainfo': table_metainfo})

        load_executor = LoadDataExecutor(plan)
        load_executor.exec()
        get_val_mock.assert_called_once_with("executor", "batch_size")
        cv_mock.assert_called_once_with(file_path, batch_size=50)
        append_mock.has_calls(call(table_metainfo, batch_frames[0]), call(
            table_metainfo, batch_frames[0]))
