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

from mock import patch
from eva.executor.load_executor import LoadDataExecutor
from eva.models.storage.batch import Batch


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
        batch = next(load_executor.exec())
        create_mock.assert_called_once_with(table_metainfo, file_path)
        self.assertEqual(batch, Batch(pd.DataFrame(
            [{'Video': file_path}])))
