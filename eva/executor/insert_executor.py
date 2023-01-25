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
import pandas as pd
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.parser.table_ref import TableValuedExpression
from eva.plan_nodes.insert_plan import InsertPlan
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger



class InsertExecutor(AbstractExecutor):
    def __init__(self, node: InsertPlan):
        super().__init__(node)
        self.catalog = CatalogManager()

    def validate(self):
        pass

    def exec(self):
        storage_engine = None
        table_obj = None
        try:    
            # Get catalog entry
            table_name = self.node.table_ref.table.table_name
            database_name = self.node.table_ref.table.database_name
            table_obj = self.catalog.get_table_catalog_entry(table_name, database_name)
            
            num_value = len(self.node.value_list)
            num_column = len(self.node.column_list)

            # TODO: Validate if it is properly divisible
            num_of_inserts = num_value//num_column

            values = []
            for num in range(num_of_inserts):
                batch = []
                for column in range(num_column):
                    batch.append(self.node.value_list[num*num_column + column].value)
                values.append(batch)
            
            column_list = []
            for i in self.node.column_list:
                column_list.append(i.col_name)
            
            dataframe = pd.DataFrame(values, columns=column_list)
            class Struct(object): pass
            batch = Struct()
            batch.frames = dataframe
            
            storage_engine = StorageEngine.factory(table_obj)
            storage_engine.write(table_obj, batch)
        except Exception as e:
            if storage_engine and table_obj:
                self._rollback_load(storage_engine, table_obj, False)
            err_msg = f"Load {self.media_type.name} failed: encountered unexpected error {str(e)}"
            logger.error(err_msg)
            raise ExecutorError(err_msg)
        else:
            yield Batch(
                pd.DataFrame(
                    [
                        f"Number of rows loaded: {str(len(self.node.value_list))}"
                    ]
                )
            )

    def _rollback_load(
        self,
        storage_engine: AbstractStorageEngine,
        table_obj: TableCatalogEntry,
        do_create: bool,
    ):
        try:
            if do_create:
                storage_engine.drop(table_obj)
        except Exception as e:
            logger.exception(
                f"Unexpected Exception {e} occured while rolling back. This is bad as the {self.media_type.name} table can be in a corrupt state. Please verify the table {table_obj} for correctness."
            )
