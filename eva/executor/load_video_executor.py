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
import numpy
from pathlib import Path

import pandas as pd

from eva.binder.binder_utils import create_video_metadata
from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.planner.load_data_plan import LoadDataPlan
from eva.storage.storage_engine import StorageEngine, VideoStorageEngine
from eva.utils.logging_manager import logger


class LoadVideoExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.upload_dir = Path(config.get_value("storage", "upload_dir"))

    def validate(self):
        pass

    def exec(self):
        """
        Read the input video using opencv and persist data
        using storage engine
        """

        video_file_path = None
        # Validate file_path
        if Path(self.node.file_path).exists():
            video_file_path = self.node.file_path
        # check in the upload directory
        else:
            video_path = Path(Path(self.upload_dir) / self.node.file_path)
            if video_path.exists():
                video_file_path = video_path

        if video_file_path is None:
            error = "Failed to find a video file at location: {}".format(
                self.node.file_path
            )
            logger.error(error)
            raise RuntimeError(error)

        # ToDo: Add logic for indexing the video file
        # Create an index of I frames to speed up random video seek

        video_metainfo = create_video_metadata(str(self.node.file_path))
        success = VideoStorageEngine.create(video_metainfo, video_file_path)

        if success:
            # dataset table should have 3 columns
            if len(self.node.table_metainfo.columns) != 3:
                raise ExecutorError(error)

            columns = self.node.table_metainfo.columns
            # filling dummy values for columns id and data
            # these are populated by video during select query
            data = {
                columns[0].name: video_metainfo.name,
                columns[1].name: 0,
                columns[2].name: numpy.array([[[]]], dtype=numpy.uint8),
            }
            print(data)
            batch = Batch(pd.DataFrame([data]))
            StorageEngine.write(self.node.table_metainfo, batch)
            yield Batch(
                pd.DataFrame(
                    [
                        f"Video {video_file_path} successfully added to dataset  {self.node.table_metainfo.name}"
                    ]
                )
            )
