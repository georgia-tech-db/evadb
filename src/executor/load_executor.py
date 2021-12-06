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

import os

import pandas as pd

from src.configuration.configuration_manager import ConfigurationManager
from src.executor.abstract_executor import AbstractExecutor
from src.models.storage.batch import Batch
from src.planner.load_data_plan import LoadDataPlan
from src.readers.opencv_reader import OpenCVReader
from src.storage.storage_engine import StorageEngine
from src.utils.metrics_manager import mm_bw_start, mm_bw_end


class LoadDataExecutor(AbstractExecutor):

    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.path_prefix = config.get_value('storage', 'path_prefix')

    def validate(self):
        pass

    def exec(self):
        """
        Read the input video using opencv and persist data
        using storage engine
        """

        # videos are persisted using (id, data) schema where id = frame_id
        # and data = frame_data. Current logic supports loading a video into
        # storage with the assumption that frame_id starts from 0. In case
        # we want to append to the existing store we have to figure out the
        # correct frame_id. It can also be a parameter based by the user.

        # We currently use create to empty existing table.
        StorageEngine.create(self.node.table_metainfo)
        num_loaded_frames = 0

        mm_bw_start(self.node.metrics, str(self.node.file_path))

        full_file_path = os.path.join(self.path_prefix, self.node.file_path)
        video_reader = OpenCVReader(
            full_file_path,
            batch_mem_size=self.node.batch_mem_size)
        for batch in video_reader.read():
            StorageEngine.write(self.node.table_metainfo, batch)
            num_loaded_frames += len(batch)

        mm_bw_end(self.node.metrics, str(self.node.file_path),
                  num_loaded_frames, os.path.getsize(full_file_path))

        yield Batch(pd.DataFrame({'Video': str(self.node.file_path),
                                  'Num Loaded Frames': num_loaded_frames},
                                 index=[0]))
