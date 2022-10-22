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
import os

import pandas as pd

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.load_data_plan import LoadDataPlan
from eva.readers.csv_reader import CSVReader
from eva.storage.storage_engine import StorageEngine


class LoadCSVExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.upload_dir = config.get_value("storage", "upload_dir")

    def validate(self):
        pass

    def exec(self):
        """
        Read the input meta file using pandas and persist data
        using storage engine
        """

        # Read the CSV file
        # converters is a dictionary of functions that convert the values
        # in the column to the desired type
        csv_reader = CSVReader(
            os.path.join(self.upload_dir, self.node.file_path),
            column_list=self.node.column_list,
            batch_mem_size=self.node.batch_mem_size,
        )

        # write with storage engine in batches
        num_loaded_frames = 0
        for batch in csv_reader.read():
            StorageEngine.write(self.node.table_metainfo, batch)
            num_loaded_frames += len(batch)

        # yield result
        df_yield_result = Batch(
            pd.DataFrame(
                {
                    "CSV": str(self.node.file_path),
                    "Number of loaded frames": num_loaded_frames,
                },
                index=[0],
            )
        )

        yield df_yield_result
