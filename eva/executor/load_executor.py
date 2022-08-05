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
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.load_csv_executor import LoadCSVExecutor
from eva.executor.load_video_executor import LoadVideoExecutor
from eva.parser.types import FileFormatType
from eva.planner.load_data_plan import LoadDataPlan


class LoadDataExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """
        Use TYPE to determine the type of data to load.
        """

        # invoke the appropriate executor
        if self.node.file_options["file_format"] == FileFormatType.VIDEO:
            executor = LoadVideoExecutor(self.node)
        elif self.node.file_options["file_format"] == FileFormatType.CSV:
            executor = LoadCSVExecutor(self.node)

        # for each batch, exec the executor
        for batch in executor.exec():
            yield batch
