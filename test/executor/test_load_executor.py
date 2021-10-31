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
import os
import pandas as pd

from mock import patch, MagicMock, call
from src.executor.load_executor import LoadDataExecutor
from src.models.storage.batch import Batch

from test.util import PATH_PREFIX


class LoadExecutorTest(unittest.TestCase):

    @patch('src.executor.load_executor.OpenCVReader')
    @patch('src.executor.load_executor.StorageEngine.create')
    @patch('src.executor.load_executor.StorageEngine.write')
    def test_should_call_opencv_reader_and_storage_engine(
            self, write_mock, create_mock, cv_mock):
        batch_frames = [list(range(5))] * 2
        attrs = {'read.return_value': batch_frames}
        cv_mock.return_value = MagicMock(**attrs)
        file_path = 'video'
        table_metainfo = 'info'
        batch_mem_size = 3000
        plan = type(
            "LoadDataPlan", (), {
                'file_path': file_path,
                'table_metainfo': table_metainfo,
                'batch_mem_size': batch_mem_size})

        load_executor = LoadDataExecutor(plan)
        batch = next(load_executor.exec())
        cv_mock.assert_called_once_with(os.path.join(PATH_PREFIX, file_path),
                                        batch_mem_size=batch_mem_size)
        create_mock.assert_called_once_with(table_metainfo)
        write_mock.has_calls(call(table_metainfo, batch_frames[0]), call(
            table_metainfo, batch_frames[1]))
        self.assertEqual(batch, Batch(pd.DataFrame(
            [{'Video': file_path, 'Num Loaded Frames': 10}])))
