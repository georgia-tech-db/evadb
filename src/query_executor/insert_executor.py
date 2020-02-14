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

from src.query_executor.abstract_executor import AbstractExecutor
from src.planner.insert_plan import InsertPlan

from src.catalog.catalog_manager import CatalogManager
from src.catalog.column_type import ColumnType

from numpy import ndarray

from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class InsertExecutor(AbstractExecutor):

    def __init__(self, node: InsertPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """
        Based on the table it constructs a valid tuple using the values provided.
        Right now we assume there are no missing values
        """
        table_id = self.node.video_id
        metadata = CatalogManager.get_metadata(table_id)
        col_id_to_val = {}
        for col_id, val in zip(self.node.column_ids, self.node.value_list):
            col_id_to_val[col_id] = val.evaluate()
        
        col_types = CatalogManager.get_column_types(table_id, None)
        col_ids = CatalogManager.get_column_ids(table_id)

        data_tuple = []
        for col_id, col_type in zip(col_ids, col_types):
            val = None
            if col_id in col_id_to_val.keys():
                val = col_id_to_val[col_id]
            try:
                if col_type == ColumnType.INTEGER:
                    data_tuple.append(int(val))
                elif col_type == ColumnType.FLOAT:
                    data_tuple.append(float(val))
                elif col_type == ColumnType.BOOLEAN:
                    data_tuple.append(bool(val))
                elif col_type == ColumnType.TEXT:
                    data_tuple.append(str(val))
                elif col_type == ColumnType.NDARRAY:
                    data_tuple.append(ndarray(val))
            except Exception as e:
                LoggingManager().log("Insert Executor failed bcz of invalid value " + e , LoggingLevel.ERROR)
                return 

        append_rows(metadata, data_tuple)

    
