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

import numpy as np
import pandas as pd

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.load_data_plan import LoadDataPlan
from eva.storage.storage_engine import StorageEngine


class LoadMetaExecutor(AbstractExecutor):

    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.path_prefix = config.get_value('storage', 'path_prefix')

    def validate(self):
        pass

    def exec(self):
        """
        Read the input meta file using pandas and persist data
        using storage engine
        """

        print(f"LoadDataExecutor: loading meta data")

        # TODO: Move to utils? Create util.py here
        # utility function to convert bbox to list of floats
        def convert_bbox(bbox):
            return np.array([np.float32(coord) for coord in bbox.split(",")])

        # Get the path to the CSV file
        csv_file_path = os.path.join(self.path_prefix, self.node.file_path)
        print(f"LoadDataExecutor: reading CSV file {csv_file_path}")

        # Read the CSV file
        meta_df = pd.read_csv(csv_file_path, converters = {"bbox" : convert_bbox})
        meta_df_len = len(meta_df)
        print(meta_df)
        print(f"LoadDataExecutor: read {meta_df_len} rows from CSV file")

        # Create a batch
        batch = Batch(meta_df)

        # Store the batch
        # TODO: Get the column types from the metadata
        # Get "bbox" column name from the metadata
        StorageEngine.write(self.node.table_metainfo, batch)

        # Return the number of frames loaded
        df_yield_result = Batch(pd.DataFrame({
            'Meta': str(self.node.file_path),
            'Number of Loaded Rows': meta_df_len,
        }, index=[0]))

        yield df_yield_result

