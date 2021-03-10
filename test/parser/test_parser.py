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
from src.parser.statement import AbstractStatement

from src.parser.statement import StatementType

from src.parser.select_statement import SelectStatement
from src.parser.create_statement import ColumnDefinition
from src.parser.create_udf_statement import CreateUDFStatement
from src.parser.load_statement import LoadDataStatement
from src.parser.insert_statement import InsertTableStatement

from src.expression.abstract_expression import ExpressionType
from src.expression.tuple_value_expression import TupleValueExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.function_expression import FunctionExpression

from src.parser.types import ParserOrderBySortType, JoinType
from src.parser.table_ref import TableRef, TableInfo, JoinNode
from src.catalog.column_type import ColumnType, NdArrayType

from pathlib import Path


class ParserTests(unittest.TestCase):

    def test_create_statement(self):
        parser = Parser()

        single_queries = []
        single_queries.append(
            """CREATE TABLE IF NOT EXISTS Persons (
                  Frame_ID INTEGER UNIQUE,
                  Frame_Data TEXT(10),
                  Frame_Value FLOAT(1000, 201),
                  Frame_Array NDARRAY UINT8(5, 100, 2432, 4324, 100)
            );""")

        for query in single_queries:
            eva_statement_list = parser.parse(query)
            self.assertIsInstance(eva_statement_list, list)
            self.assertEqual(len(eva_statement_list), 1)
            self.assertIsInstance(
                eva_statement_list[0], AbstractStatement)

    def test_single_statement_queries(self):
        parser = Parser()

        single_queries = []
        single_queries.append("SELECT CLASS FROM TAIPAI;")
        single_queries.append("SELECT CLASS FROM TAIPAI WHERE CLASS = 'VAN';")
        single_queries.append("SELECT CLASS,REDNESS FROM TAIPAI \
            WHERE CLASS = 'VAN' AND REDNESS > 20;")
        single_queries.append("SELECT CLASS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;")
        single_queries.append("SELECT CLASS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;")

        for query in single_queries:
            eva_statement_list = parser.parse(query)

            self.assertIsInstance(eva_statement_list, list)
            self.assertEqual(len(eva_statement_list), 1)
            self.assertIsInstance(
                eva_statement_list[0], AbstractStatement)

    def test_multiple_statement_queries(self):
        parser = Parser()

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
                eva_statement_list[0], AbstractStatement)
            self.assertIsInstance(
                eva_statement_list[1], AbstractStatement)

    def test_select_statement(self):
        parser = Parser()
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

    def test_select_union_statement(self):
        parser = Parser()
        select_union_query = "SELECT CLASS, REDNESS FROM TAIPAI \
            UNION ALL SELECT CLASS, REDNESS FROM SHANGHAI;"
        eva_statement_list = parser.parse(select_union_query)
        select_stmt = eva_statement_list[0]
        self.assertIsNotNone(select_stmt.union_link)
        self.assertEqual(select_stmt.union_all, True)
        second_select_stmt = select_stmt.union_link
        self.assertIsNone(second_select_stmt.union_link)

    def test_select_statement_class(self):
        ''' Testing setting different clauses for Select
        Statement class
        Class: SelectStatement'''

        select_stmt_new = SelectStatement()
        parser = Parser()

        select_query_new = "SELECT CLASS, REDNESS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 400 ) OR REDNESS > 700;"
        eva_statement_list = parser.parse(select_query_new)
        select_stmt = eva_statement_list[0]

        select_stmt_new.where_clause = select_stmt.where_clause
        select_stmt_new.target_list = select_stmt.target_list
        select_stmt_new.from_table = select_stmt.from_table

        self.assertEqual(
            select_stmt_new.where_clause, select_stmt.where_clause)
        self.assertEqual(
            select_stmt_new.target_list, select_stmt.target_list)
        self.assertEqual(
            select_stmt_new.from_table, select_stmt.from_table)
        self.assertEqual(str(select_stmt_new), str(select_stmt))

    def test_select_statement_orderby_class(self):
        '''Testing order by clause in select statement
        Class: SelectStatement'''

        parser = Parser()

        select_query = "SELECT CLASS, REDNESS FROM TAIPAI \
                    WHERE (CLASS = 'VAN' AND REDNESS < 400 ) OR REDNESS > 700 \
                    ORDER BY CLASS, REDNESS DESC;"
        # if orderby sort_type (ASC/DESC) not provided, should default to ASC

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

        # orderby_clause
        self.assertIsNotNone(select_stmt.orderby_list)
        self.assertEqual(len(select_stmt.orderby_list), 2)
        self.assertEqual(select_stmt.orderby_list[0][0].col_name, 'CLASS')
        self.assertEqual(
            select_stmt.orderby_list[0][1], ParserOrderBySortType.ASC)
        self.assertEqual(select_stmt.orderby_list[1][0].col_name, 'REDNESS')
        self.assertEqual(
            select_stmt.orderby_list[1][1], ParserOrderBySortType.DESC)

    def test_select_statement_limit_class(self):
        '''Testing limit clause in select statement
        Class: SelectStatement'''

        parser = Parser()

        select_query = "SELECT CLASS, REDNESS FROM TAIPAI \
                    WHERE (CLASS = 'VAN' AND REDNESS < 400 ) OR REDNESS > 700 \
                    ORDER BY CLASS, REDNESS DESC LIMIT 3;"

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

        # orderby_clause
        self.assertIsNotNone(select_stmt.orderby_list)
        self.assertEqual(len(select_stmt.orderby_list), 2)
        self.assertEqual(select_stmt.orderby_list[0][0].col_name, 'CLASS')
        self.assertEqual(
            select_stmt.orderby_list[0][1], ParserOrderBySortType.ASC)
        self.assertEqual(select_stmt.orderby_list[1][0].col_name, 'REDNESS')
        self.assertEqual(
            select_stmt.orderby_list[1][1], ParserOrderBySortType.DESC)

        # limit_count
        self.assertIsNotNone(select_stmt.limit_count)
        self.assertEqual(select_stmt.limit_count, ConstantValueExpression(3))

    def test_table_ref(self):
        ''' Testing table info in TableRef
            Class: TableInfo
        '''
        table_info = TableInfo('TAIPAI', 'Schema', 'Database')
        table_ref_obj = TableRef(table_info)
        select_stmt_new = SelectStatement()
        select_stmt_new.from_table = table_ref_obj
        self.assertEqual(
            select_stmt_new.from_table.table_info.table_name,
            'TAIPAI')
        self.assertEqual(
            select_stmt_new.from_table.table_info.schema_name,
            'Schema')
        self.assertEqual(
            select_stmt_new.from_table.table_info.database_name,
            'Database')

    def test_insert_statement(self):
        parser = Parser()
        insert_query = """INSERT INTO MyVideo (Frame_ID, Frame_Path)
                                    VALUES    (1, '/mnt/frames/1.png');
                        """
        expected_stmt = InsertTableStatement(
            TableRef(
                TableInfo('MyVideo')), [
                TupleValueExpression('Frame_ID'),
                TupleValueExpression('Frame_Path')], [
                ConstantValueExpression(1),
                ConstantValueExpression('/mnt/frames/1.png')])
        eva_statement_list = parser.parse(insert_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.INSERT)

        insert_stmt = eva_statement_list[0]
        self.assertEqual(insert_stmt, expected_stmt)

    def test_create_udf_statement(self):
        parser = Parser()
        create_udf_query = """CREATE UDF FastRCNN
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (Labels NDARRAY STR(10), Bbox NDARRAY UINT8(10, 4))
                  TYPE  Classification
                  IMPL  'data/fastrcnn.py';
        """

        expected_stmt = CreateUDFStatement(
            'FastRCNN', False, [
                ColumnDefinition(
                    'Frame_Array', ColumnType.NDARRAY, NdArrayType.UINT8,
                    [3, 256, 256])], [
                ColumnDefinition(
                    'Labels', ColumnType.NDARRAY, NdArrayType.STR, [10]),
                ColumnDefinition(
                    'Bbox', ColumnType.NDARRAY, NdArrayType.UINT8, [10, 4])],
            Path('data/fastrcnn.py'), 'Classification')
        eva_statement_list = parser.parse(create_udf_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(
            eva_statement_list[0].stmt_type,
            StatementType.CREATE_UDF)

        create_udf_stmt = eva_statement_list[0]

        self.assertEqual(create_udf_stmt, expected_stmt)

    def test_load_data_statement(self):
        parser = Parser()
        load_data_query = """LOAD DATA INFILE 'data/video.mp4' INTO MyVideo;"""
        expected_stmt = LoadDataStatement(
            TableRef(
                TableInfo('MyVideo')),
            Path('data/video.mp4'))
        eva_statement_list = parser.parse(load_data_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(
            eva_statement_list[0].stmt_type,
            StatementType.LOAD_DATA)

        load_data_stmt = eva_statement_list[0]
        self.assertEqual(load_data_stmt, expected_stmt)

    def test_nested_select_statement(self):
        parser = Parser()
        sub_query = """SELECT CLASS FROM TAIPAI WHERE CLASS = 'VAN'"""
        nested_query = """SELECT ID FROM ({});""".format(sub_query)
        parsed_sub_query = parser.parse(sub_query)[0]
        actual_stmt = parser.parse(nested_query)[0]
        self.assertEqual(actual_stmt.stmt_type, StatementType.SELECT)
        self.assertEqual(actual_stmt.target_list[0].col_name, 'ID')
        self.assertEqual(actual_stmt.from_table, parsed_sub_query)

        sub_query = """SELECT Yolo(frame).bbox FROM autonomous_vehicle_1
                              WHERE Yolo(frame).label = 'vehicle'"""
        nested_query = """SELECT Licence_plate(bbox) FROM
                            ({})
                          WHERE Is_suspicious(bbox) = 1 AND
                                Licence_plate(bbox) = '12345';
                      """.format(sub_query)
        query = """SELECT Licence_plate(bbox) FROM TAIPAI
                    WHERE Is_suspicious(bbox) = 1 AND
                        Licence_plate(bbox) = '12345';
                """
        query_stmt = parser.parse(query)[0]
        actual_stmt = parser.parse(nested_query)[0]
        sub_query_stmt = parser.parse(sub_query)[0]
        self.assertEqual(actual_stmt.from_table, sub_query_stmt)
        self.assertEqual(actual_stmt.where_clause, query_stmt.where_clause)
        self.assertEqual(actual_stmt.target_list, query_stmt.target_list)

    def test_should_return_false_for_unequal_expression(self):
        table = TableRef(TableInfo('MyVideo'))
        load_stmt = LoadDataStatement(table, Path('data/video.mp4'))
        insert_stmt = InsertTableStatement(table)
        create_udf = CreateUDFStatement(
            'udf', False, [
                ColumnDefinition(
                    'frame', ColumnType.NDARRAY, NdArrayType.UINT8,
                    [3, 256, 256])], [
                ColumnDefinition(
                    'labels', ColumnType.NDARRAY, NdArrayType.STR, [10])],
            Path('data/fastrcnn.py'), 'Classification')
        select_stmt = SelectStatement()
        self.assertNotEqual(load_stmt, insert_stmt)
        self.assertNotEqual(insert_stmt, load_stmt)
        self.assertNotEqual(create_udf, insert_stmt)
        self.assertNotEqual(select_stmt, create_udf)

    def test_should_handle_lateral_join(self):
        parser = Parser()
        query = """SELECT id, frame FROM DETRAC,
                LATERAL UNNEST(ObjDet(frame)) WHERE id < 10;"""

        right = FunctionExpression(func=None, name='UNNEST')
        child = FunctionExpression(func=None, name='ObjDet')
        child.append_child(TupleValueExpression('frame'))
        right.append_child(child)
        left = TableRef(TableInfo('DETRAC'))
        expected_from_clause = TableRef(join=JoinNode(
            left=left, right=right, join_type=JoinType.LATERAL_JOIN))
        query_stmt = parser.parse(query)[0]
        self.assertEqual(query_stmt.from_table, expected_from_clause)
