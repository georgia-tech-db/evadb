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
import base64
import os

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.load_csv_executor import LoadCSVExecutor
from eva.executor.load_video_executor import LoadVideoExecutor
from eva.parser.types import FileFormatType
from eva.planner.upload_plan import UploadPlan


class UploadExecutor(AbstractExecutor):
    def __init__(self, node: UploadPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.upload_dir = config.get_value("storage", "upload_dir")

    def validate(self):
        pass

    def exec(self):
        """
        Upload the video blob into the location defined by 'path'
        on the server. The video blob is in base64 format, so
        it will first be decoded by the executor and then saved
        at the specified path with a predefined prefix
        """

        video_blob = self.node.video_blob
        path = self.node.file_path
        video_bytes = base64.b64decode(video_blob[1:])
        with open(os.path.join(self.upload_dir, path), "wb") as f:
            f.write(video_bytes)

        # invoke the appropriate executor
        if self.node.file_options["file_format"] == FileFormatType.VIDEO:
            executor = LoadVideoExecutor(self.node)
        elif self.node.file_options["file_format"] == FileFormatType.CSV:
            executor = LoadCSVExecutor(self.node)

        # for each batch, exec the executor
        for batch in executor.exec():
            yield batch

        # Delete the video from ~/.eva ?
        # os.remove(os.path.join(EVA_DEFAULT_DIR, path))
