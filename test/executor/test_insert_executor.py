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
from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.planner.insert_plan import InsertPlan
from src.planner.create_plan import CreatePlan
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.column_type import ColumnType
from src.parser.table_ref import TableRef, TableInfo
from src.query_executor.insert_executor import InsertExecutor
from src.query_executor.create_executor import CreateExecutor
from src.storage.dataframe import load_dataframe


class InsertExecutorTest(unittest.TestCase):
    # integration test
    def test_should_insert_row_in_table(self):
        dummy_info = TableInfo('MyVideo')
        dummy_table = TableRef(dummy_info)

        columns = [DataFrameColumn('Frame_ID', ColumnType.INTEGER),
                   DataFrameColumn('Frame_Path', ColumnType.TEXT,
                                   array_dimensions=50)]
        plan_node = CreatePlan(dummy_table, columns, False)

        createExec = CreateExecutor(plan_node)
        url = createExec.exec()

        parser = Parser()
        insert_query = """INSERT INTO MyVideo (Frame_ID, Frame_Path)
                                    VALUES    (1, '/mnt/frames/1.png');
                        """

        eva_statement_list = parser.parse(insert_query)
        insert_stmt = eva_statement_list[0]
        convertor = StatementToPlanConvertor()
        convertor.visit(insert_stmt)
        logical_plan_node = convertor.plan
        print("logical", logical_plan_node)
        phy_plan_node = InsertPlan(
            logical_plan_node.video_catalog_id,
            logical_plan_node.column_list,
            logical_plan_node.value_list)

        insertExec = InsertExecutor(phy_plan_node)
        insertExec.exec()

        # test if we have a added the in our storage
        df = load_dataframe(url)
        self.assertEqual(df.collect()[0][0], 1)
        self.assertEqual(df.collect()[0][1], "'/mnt/frames/1.png'")

        # ToDo call drop this table
        # Add support in catalog and spark


if __name__ == "__main__":
    unittest.main()
