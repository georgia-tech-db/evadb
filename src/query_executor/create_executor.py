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

from src.catalog.catalog_manager import catalogManager
from src.catalog.df_schema import DataFrameSchema
from src.planner.create_plan import CreatePlan
from src.query_executor.abstract_executor import AbstractExecutor
from src.storage.dataframe import create_dataframe


class CreateExecutor(AbstractExecutor):

    def __init__(self, node: CreatePlan):
        super().__init__(node)
        self._table_name = node.table_name
        self._file_url = node.file_url
        self._schema_tuples = node.schema_tuples

    def validate(self):
        pass

    def exec(self):
        """
        Based on the table it constructs a valid tuple using the values
        provided.
        Right now we assume there are no missing values
        """

        metadata = catalogManager.create_metadata(self._table_name,
                                                  self._file_url)

        col_list = []
        for colname, coltype in self._schema_tuples:
            col_list.append(catalogManager.create_column(colname, coltype,
                                                         metadata.get_id()))

        df_schema = DataFrameSchema(self._table_name, col_list)
        metadata.set_schema(df_schema)

        create_dataframe(metadata)
