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
from pathlib import Path

import pandas as pd

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.load_data_plan import LoadDataPlan
from eva.storage.storage_engine import VideoStorageEngine
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

        VideoStorageEngine.create(self.node.table_metainfo, if_not_exists=True)
        success = VideoStorageEngine.write(
            self.node.table_metainfo,
            Batch(pd.DataFrame([{"video_file_path": str(video_file_path)}])),
        )

        # ToDo: Add logic for indexing the video file
        # Create an index of I frames to speed up random video seek
        if success:
            yield Batch(
                pd.DataFrame(
                    [f"Video successfully added at location: {video_file_path}"]
                )
            )
