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
from unittest.mock import patch

from src.eva.catalog.models.df_metadata import DataFrameMetadata
from src.eva.executor.disk_based_storage_executor import DiskStorageExecutor
from src.eva.planner.storage_plan import StoragePlan


class DiskStorageExecutorTest(unittest.TestCase):

    @unittest.skip("disable test due to deprication")
    @patch('eva.executor.disk_based_storage_executor.Loader')
    def test_calling_storage_executor_should_return_batches(self, mock_class):
        class_instance = mock_class.return_value

        video_info = DataFrameMetadata('dataset', 'dummy.avi')
        batch_mem_size = 3000
        storage_plan = StoragePlan(video_info, batch_mem_size)

        executor = DiskStorageExecutor(storage_plan)

        class_instance.load.return_value = range(5)
        actual = list(executor.exec())

        mock_class.assert_called_once_with(video_info,
                                           batch_mem_size=(
                                               storage_plan.batch_mem_size),
                                           limit=storage_plan.limit,
                                           offset=storage_plan.offset,
                                           skip_frames=(
                                               storage_plan.skip_frames),
                                           total_shards=0,
                                           curr_shard=0
                                           )
        class_instance.load.assert_called_once()
        self.assertEqual(list(range(5)), actual)
