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
import base64

from eva.planner.upload_plan import UploadPlan
from eva.executor.abstract_executor import AbstractExecutor

from eva.configuration.configuration_manager import ConfigurationManager


class UploadExecutor(AbstractExecutor):

    def __init__(self, node: UploadPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.path_prefix = config.get_value('storage', 'path_prefix')

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
        with open(os.path.join(self.path_prefix, path), 'wb') as f:
            f.write(video_bytes)
