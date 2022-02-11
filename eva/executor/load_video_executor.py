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

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.load_data_plan import LoadDataPlan
from eva.readers.opencv_reader import OpenCVReader
from eva.storage.storage_engine import StorageEngine


class LoadVideoExecutor(AbstractExecutor):

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
        
        # We currently use create to empty existing table.
        StorageEngine.create(self.node.table_metainfo)

        # read the video with opencv
        video_reader = OpenCVReader(
            os.path.join(self.path_prefix, self.node.file_path),
            batch_mem_size=self.node.batch_mem_size
        )

        # write with storage engine in batches
        num_loaded_frames = 0
        for batch in video_reader.read():
            StorageEngine.write(self.node.table_metainfo, batch)
            num_loaded_frames += len(batch)

        # yield result
        df_yield_result = Batch(pd.DataFrame({
                'Video': str(self.node.file_path),
                'Number of Loaded Frames': num_loaded_frames
            },
        index=[0]))

        yield df_yield_result