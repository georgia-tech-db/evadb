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
from evadb.executor.executor_utils import (
    create_table_catalog_entry_for_native_table,
    handle_if_not_exists,
)
from evadb.plan_nodes.create_plan import CreatePlan
from evadb.storage.storage_engine import StorageEngine
from evadb.utils.logging_manager import logger


class CreateExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreatePlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        # create a table in the ative database if set
        is_native_table = self.node.table_info.database_name is not None
        check_if_exists = False
        # if exists only supported for evadb tables
        if not is_native_table:
            check_if_exists = handle_if_not_exists(
                self.catalog(), self.node.table_info, self.node.if_not_exists
            )

        if not check_if_exists:
            create_table_done = False
            logger.debug(f"Creating table {self.node.table_info}")

            if not is_native_table:
                catalog_entry = self.catalog().create_and_insert_table_catalog_entry(
                    self.node.table_info, self.node.column_list
                )
            else:
                catalog_entry = create_table_catalog_entry_for_native_table(
                    self.node.table_info, self.node.column_list
                )
            storage_engine = StorageEngine.factory(self.db, catalog_entry)

            try:
                storage_engine.create(table=catalog_entry)
                create_table_done = True
                if self.children != []:
                    assert (
                        len(self.children) == 1
                    ), "Create table from query expects 1 child, finds {}".format(
                        len(self.children)
                    )
                    child = self.children[0]

                    # Populate the table
                    for batch in child.exec():
                        batch.drop_column_alias()
                        storage_engine.write(catalog_entry, batch)
            except Exception as e:
                # rollback if the create call fails
                if create_table_done:
                    storage_engine.drop(catalog_entry)
                raise e
