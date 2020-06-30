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

from numpy import ndarray

from src.catalog.catalog_manager import CatalogManager
from src.catalog.column_type import ColumnType
from src.planner.load_data_plan import LoadDataPlan
from src.executor.abstract_executor import AbstractExecutor
from src.storage.dataframe import append_rows
from src.loaders.video_loader import VideoLoader
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class LoadDataExecutor(AbstractExecutor):

    def __init__(self, node: LoadDataPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """
        Call the video loader to construct data frames (frame_id, frame_Data) 
        which are stored in the database 
        """
        # trying arbitrary batch size
        video_loader = VideoLoader(self.node.file_path, batch_size=50)
        for batch in video_loader:
            append_rows(self.node.table_metainfo, batch)
        
