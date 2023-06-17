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
import pandas as pd

from evadb.catalog.catalog_type import TableType
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.insert_plan import InsertPlan
from evadb.storage.storage_engine import StorageEngine


class InsertExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: InsertPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        storage_engine = None
        table_catalog_entry = None

        # Get catalog entry
        table_name = self.node.table_ref.table.table_name
        database_name = self.node.table_ref.table.database_name
        table_catalog_entry = self.catalog().get_table_catalog_entry(
            table_name, database_name
        )

        # Implemented only for STRUCTURED_DATA
        assert (
            table_catalog_entry.table_type == TableType.STRUCTURED_DATA
        ), "INSERT only implemented for structured data"

        values_to_insert = [val_node.value for val_node in self.node.value_list]
        tuple_to_insert = tuple(values_to_insert)
        columns_to_insert = [col_node.name for col_node in self.node.column_list]

        # Adding all values to Batch for insert
        dataframe = pd.DataFrame([tuple_to_insert], columns=columns_to_insert)
        batch = Batch(dataframe)

        storage_engine = StorageEngine.factory(self.db, table_catalog_entry)
        storage_engine.write(table_catalog_entry, batch)

        yield Batch(
            pd.DataFrame([f"Number of rows loaded: {str(len(values_to_insert))}"])
        )
