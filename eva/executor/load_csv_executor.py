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
from eva.readers.csv_reader import CSVReader
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


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

        csv_file_path = None
        # Validate file_path
        if Path(self.node.file_path).exists():
            csv_file_path = self.node.file_path
        # check in the upload directory
        else:
            csv_path = Path(Path(self.upload_dir) / self.node.file_path)
            if csv_path.exists():
                csv_file_path = csv_path

        if csv_file_path is None:
            error = "Failed to find a video file at location: {}".format(
                self.node.file_path
            )
            logger.error(error)
            raise RuntimeError(error)

        # Read the CSV file
        # converters is a dictionary of functions that convert the values
        # in the column to the desired type
        csv_reader = CSVReader(
            csv_file_path,
            column_list=self.node.column_list,
            batch_mem_size=self.node.batch_mem_size,
        )

        # write with storage engine in batches
        num_loaded_frames = 0
        for batch in csv_reader.read():
            StorageEngine.write(self.node.table_metainfo, batch)
            num_loaded_frames += len(batch)

        # yield result
        yield Batch(
            pd.DataFrame([f"CSV successfully loaded at location: {csv_file_path}"])
        )
