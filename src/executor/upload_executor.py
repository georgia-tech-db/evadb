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

from src.planner.upload_plan import UploadPlan
from src.executor.abstract_executor import AbstractExecutor


class UploadExecutor(AbstractExecutor):

    def __init__(self, node: UploadPlan):
        super().__init__(node)

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
        print("Write data to disk here")
