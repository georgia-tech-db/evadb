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
import unittest
from src.planner.create_plan import CreatePlan
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.column_type import ColumnType
from src.catalog.models.base_model import drop_db
from src.parser.table_ref import TableRef, TableInfo
from src.executor.create_executor import CreateExecutor
from src.storage import StorageEngine

class CreateExecutorTest(unittest.TestCase):

    def setUp(self):
        pass

    # integration test
    @unittest.skip("we need drop functionality before we can enable")
    def test_create_executor_should_create_table_in_storage(self):
        dummy_info = TableInfo('dummy')
        dummy_table = TableRef(dummy_info)

        columns = [DataFrameColumn('id', ColumnType.INTEGER),
                   DataFrameColumn('name', ColumnType.TEXT,
                                   array_dimensions=50)]
        plan_node = CreatePlan(dummy_table, columns, False)

        createExec = CreateExecutor(plan_node)
        metadata = createExec.exec()

        row_iter = StorageEngine.read(metadata)
        self.assertFalse(any(True for _ in row_iter))

        # ToDo call drop this table
        # Add support in catalog and spark
