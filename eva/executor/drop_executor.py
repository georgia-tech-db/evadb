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

from eva.catalog.catalog_manager import CatalogManager
from eva.planner.drop_plan import DropPlan
from eva.executor.abstract_executor import AbstractExecutor


class DropExecutor(AbstractExecutor):

    def __init__(self, node: DropPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """ Drop table executor """

        # TODO: Use if exists
        # tables_to_drop = self.node.table_refs
        tables_to_drop_ids = self.node.table_ids
        # if_exists = self.node.if_exists

        for table_id in tables_to_drop_ids:
            CatalogManager()._dataset_service.delete_dataset_by_id(table_id)
