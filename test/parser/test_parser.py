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

from src.parser.eva_parser import EvaQLParser
from src.parser.eva_statement import EvaStatement
from src.parser.eva_statement import StatementType

from src.expression.abstract_expression import ExpressionType
from src.parser.table_ref import TableRef


class ParserTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_eva_parser(self):
        parser = EvaQLParser()
        print(parser)

        parser = EvaQLParser()
        print(parser)

        single_queries = []
        single_queries.append("SELECT CLASS FROM TAIPAI;")
        single_queries.append("SELECT CLASS FROM TAIPAI WHERE CLASS = 'VAN';")
        single_queries.append("SELECT CLASS,REDNESS FROM TAIPAI \
            WHERE CLASS = 'VAN' AND REDNESS > 20;")
        single_queries.append("SELECT CLASS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;")
        single_queries.append("SELECT CLASS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;")

        #single_queries.append("CREATE TABLE Persons ( PersonID INTEGER);")

        for query in single_queries:
            eva_statement_list = parser.parse(query)

            print(eva_statement_list[0])

            self.assertIsInstance(eva_statement_list, list)
            self.assertEqual(len(eva_statement_list), 1)
            self.assertIsInstance(
                eva_statement_list[0], EvaStatement)

        multiple_queries = []
        multiple_queries.append("SELECT CLASS FROM TAIPAI \
            WHERE CLASS = 'VAN' AND REDNESS < 300  OR REDNESS > 500; \
            SELECT REDNESS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS = 300)")

        for query in multiple_queries:
            eva_statement_list = parser.parse(query)
            self.assertIsInstance(eva_statement_list, list)
            self.assertEqual(len(eva_statement_list), 2)
            self.assertIsInstance(
                eva_statement_list[0], EvaStatement)
            self.assertIsInstance(
                eva_statement_list[1], EvaStatement)

    def test_select_parser(self):
        parser = EvaQLParser()
        select_query = "SELECT CLASS, REDNESS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;"
        eva_statement_list = parser.parse(select_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.SELECT)

        select_stmt = eva_statement_list[0]

        # target List
        self.assertIsNotNone(select_stmt.target_list)
        self.assertEqual(len(select_stmt.target_list), 2)
        self.assertEqual(
            select_stmt.target_list[0].etype, ExpressionType.TUPLE_VALUE)
        self.assertEqual(
            select_stmt.target_list[1].etype, ExpressionType.TUPLE_VALUE)

        # from_table
        self.assertIsNotNone(select_stmt.from_table)
        self.assertIsInstance(select_stmt.from_table, TableRef)
        self.assertEqual(
            select_stmt.from_table.table_info.table_name, 'TAIPAI')

        # where_clause
        self.assertIsNotNone(select_stmt.where_clause)
        # other tests should go in expression testing


if __name__ == '__main__':
    unittest.main()
