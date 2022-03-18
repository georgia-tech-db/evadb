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

import pandas as pd

from eva.planner.load_data_plan import LoadDataPlan
from eva.executor.abstract_executor import AbstractExecutor
from eva.storage.storage_engine import VideoStorageEngine
from eva.models.storage.batch import Batch


class LoadDataExecutor(AbstractExecutor):

    def __init__(self, node: LoadDataPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        success = VideoStorageEngine.create(
            self.node.table_metainfo, self.node.file_path)

        # ToDo: Add logic for indexing the video file
        # Create an index of I frames to speed up random video seek
        if success:
            yield Batch(pd.DataFrame({'Video': str(self.node.file_path)},
                                     index=[0]))
