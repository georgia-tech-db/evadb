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
from evadb.plan_nodes.rename_plan import RenamePlan
from evadb.storage.storage_engine import StorageEngine


class RenameExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: RenamePlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        """rename table executor

        Calls the catalog to modified catalog entry corresponding to the table.
        """
        obj = self.node.old_table.table.table_obj
        storage_engine = StorageEngine.factory(self.db, obj)
        storage_engine.rename(obj, self.node.new_name)
