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
import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.load_csv_executor import LoadCSVExecutor
from eva.executor.load_video_executor import LoadVideoExecutor
from eva.models.storage.batch import Batch
from eva.parser.types import FileFormatType
from eva.planner.load_data_plan import LoadDataPlan
from eva.storage.storage_engine import StorageEngine


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

        batch = executor.exec().next()
        """
        assert (
            len(self.node.dataset_metainfo.columns) == 1
        ), f"Dataset expects one column; found {self.node.dataset_metainfo.columns}"
        """
        column_name = self.node.dataset_metainfo.columns[0].name
        """
        columns = self.node.dataset_metainfo.columns
            # filling dummy values for columns id and data
            # these are populated by video during select query
        data = {
            columns[0].name: video_metainfo.name,
            columns[1].name: 0,
            columns[2].name: numpy.array([[[]]], dtype=numpy.uint8),
        }
        """
        batch = Batch(pd.DataFrame([{column_name: self.node.table_metainfo.name}]))
        StorageEngine.write(self.node.dataset_metainfo, batch)
        yield batch + Batch(
            pd.DataFrame(
                [
                    f"Table {self.node.table_metainfo.name} successfully added to Dataset {self.node.dataset_metainfo.name}"
                ]
            )
        )
