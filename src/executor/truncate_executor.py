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
from src.planner.truncate_plan import TruncatePlan
from src.executor.abstract_executor import AbstractExecutor
from src.storage.storage_engine import StorageEngine


class TruncateExecutor(AbstractExecutor):

    def __init__(self, node: TruncatePlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """truncate table executor
        """
        table_id = self.node.table_id
        
        old_name, new_name, new_metadata= CatalogManager().truncate_table_metadata(table_id)
        StorageEngine.create(table=new_metadata)

        CatalogManager()._dataset_service.delete_dataset_by_id(table_id)

        metadata_id = CatalogManager()._dataset_service.dataset_by_name(new_name)
        CatalogManager().rename_table(old_name, metadata_id)
        
