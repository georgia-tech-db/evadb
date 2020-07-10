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

from src.catalog.catalog_manager import CatalogManager
from src.planner.create_plan import CreatePlan
from src.executor.abstract_executor import AbstractExecutor
from src.storage import StorageEngine
import tempfile
import os.path


class CreateExecutor(AbstractExecutor):

    def __init__(self, node: CreatePlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """Create table executor

        Calls the catalog to create metadata corresponding to the table.
        Calls the storage to create a spark dataframe from the metadata object.
        """
        if (self.node.if_not_exists):
            # check catalog if we already have this table
            return
        # Generate a file_url to be used for table
        # hard coding a path right now, should write a auto-generator
        table_name = self.node.video_ref.table_info.table_name
        file_url = os.path.join(tempfile.gettempdir(), table_name)
        file_url = 'file://' + file_url
        metadata = CatalogManager().create_metadata(table_name,
                                                    file_url,
                                                    self.node.column_list)

        StorageEgine.create(metadata)
        return file_url
