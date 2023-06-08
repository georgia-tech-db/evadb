# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.load_csv_executor import LoadCSVExecutor
from evadb.executor.load_multimedia_executor import LoadMultimediaExecutor
from evadb.parser.types import FileFormatType
from evadb.plan_nodes.load_data_plan import LoadDataPlan


class LoadDataExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: LoadDataPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        """
        Use TYPE to determine the type of data to load.
        """

        # invoke the appropriate executor
        if self.node.file_options["file_format"] in [
            FileFormatType.VIDEO,
            FileFormatType.IMAGE,
            FileFormatType.DOCUMENT,
            FileFormatType.PDF,
        ]:
            executor = LoadMultimediaExecutor(self.db, self.node)
        elif self.node.file_options["file_format"] == FileFormatType.CSV:
            executor = LoadCSVExecutor(self.db, self.node)

        # for each batch, exec the executor
        for batch in executor.exec():
            yield batch
