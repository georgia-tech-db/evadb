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
from evadb.executor.executor_utils import handle_if_not_exists
from evadb.plan_nodes.create_mat_view_plan import CreateMaterializedViewPlan
from evadb.storage.storage_engine import StorageEngine


class CreateMaterializedViewExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreateMaterializedViewPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        """Create materialized view executor"""
        if not handle_if_not_exists(
            self.catalog(), self.node.view, self.node.if_not_exists
        ):
            assert (
                len(self.children) == 1
            ), "Create materialized view expects 1 child, finds {}".format(
                len(self.children)
            )
            child = self.children[0]

            view_catalog_entry = self.catalog().create_and_insert_table_catalog_entry(
                self.node.view, self.node.columns
            )
            storage_engine = StorageEngine.factory(self.db, view_catalog_entry)
            storage_engine.create(table=view_catalog_entry)

            # Populate the view
            for batch in child.exec():
                batch.drop_column_alias()
                storage_engine.write(view_catalog_entry, batch)
