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
import unittest
from pathlib import Path

from eva.catalog.column_type import ColumnType, NdArrayType
from eva.expression.abstract_expression import ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.alias import Alias
from eva.parser.create_mat_view_statement import CreateMaterializedViewStatement
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition
from eva.parser.create_udf_statement import CreateUDFStatement
from eva.parser.drop_statement import DropTableStatement
from eva.parser.drop_udf_statement import DropUDFStatement
from eva.parser.insert_statement import InsertTableStatement
from eva.parser.load_statement import LoadDataStatement
from eva.parser.parser import Parser
from eva.parser.rename_statement import RenameTableStatement
from eva.parser.select_statement import SelectStatement
from eva.parser.statement import AbstractStatement, StatementType
from eva.parser.table_ref import JoinNode, TableInfo, TableRef, TableValuedExpression
from eva.parser.types import FileFormatType, JoinType, ParserOrderBySortType
from eva.parser.upload_statement import UploadStatement


class ParserTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_explain_dml_statement(self):
        parser = Parser()

        explain_query = "EXPLAIN SELECT CLASS FROM TAIPAI;"
        eva_statement_list = parser.parse(explain_query)

        # check explain stmt itself
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.EXPLAIN)

        # check inner stmt
        inner_stmt = eva_statement_list[0].explainable_stmt
        self.assertEqual(inner_stmt.stmt_type, StatementType.SELECT)

        # check inner stmt from
        self.assertIsNotNone(inner_stmt.from_table)
        self.assertIsInstance(inner_stmt.from_table, TableRef)
        self.assertEqual(inner_stmt.from_table.table.table_name, "TAIPAI")

    def test_explain_ddl_statement(self):
        parser = Parser()

        select_query = """SELECT id, FastRCNNObjectDetector(frame).labels FROM MyVideo
                        WHERE id<5; """
        explain_query = "EXPLAIN CREATE MATERIALIZED VIEW uadtrac_fastRCNN (id, labels) AS {}".format(
            select_query
        )

        eva_statement_list = parser.parse(explain_query)

        # check explain stmt itself
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.EXPLAIN)

        # check inner stmt
        inner_stmt = eva_statement_list[0].explainable_stmt
        self.assertEqual(inner_stmt.stmt_type, StatementType.CREATE_MATERIALIZED_VIEW)

        # check inner stmt from
        self.assertIsNotNone(
            inner_stmt.view_ref, TableRef(TableInfo("uadetrac_fastRCNN"))
        )

    def test_create_statement(self):
        parser = Parser()

        single_queries = []
        single_queries.append(
            """CREATE TABLE IF NOT EXISTS Persons (
                  Frame_ID INTEGER UNIQUE,
                  Frame_Data TEXT(10),
                  Frame_Value FLOAT(1000, 201),
                  Frame_Array NDARRAY UINT8(5, 100, 2432, 4324, 100)
            );"""
        )

        for query in single_queries:
            eva_statement_list = parser.parse(query)
            self.assertIsInstance(eva_statement_list, list)
            self.assertEqual(len(eva_statement_list), 1)
            self.assertIsInstance(eva_statement_list[0], AbstractStatement)

    def test_rename_statement(self):
        parser = Parser()
        rename_queries = "RENAME TABLE student TO student_info"
        expected_stmt = RenameTableStatement(
            TableRef(TableInfo("student")), TableInfo("student_info")
        )
        eva_statement_list = parser.parse(rename_queries)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.RENAME)

        rename_stmt = eva_statement_list[0]
        self.assertEqual(rename_stmt, expected_stmt)

    def test_drop_table_statement(self):
        parser = Parser()
        drop_queries = "DROP TABLE student_info"
        expected_stmt = DropTableStatement([TableRef(TableInfo("student_info"))], False)
        eva_statement_list = parser.parse(drop_queries)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.DROP)
        drop_stmt = eva_statement_list[0]
        self.assertEqual(drop_stmt, expected_stmt)

    def test_drop_udf_statement(self):
        parser = Parser()
        drop_udf_query = """DROP UDF FastRCNN;"""

        expected_stmt = DropUDFStatement("FastRCNN", False)
        eva_statement_list = parser.parse(drop_udf_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.DROP_UDF)
        drop_udf_stmt = eva_statement_list[0]
        self.assertEqual(drop_udf_stmt, expected_stmt)

    def test_drop_udf_statement_str(self):
        drop_udf_query1 = """DROP UDF MyUDF;"""
        drop_udf_query2 = """DROP UDF IF EXISTS MyUDF;"""
        expected_stmt1 = DropUDFStatement("MyUDF", False)
        expected_stmt2 = DropUDFStatement("MyUDF", True)
        self.assertEqual(str(expected_stmt1), drop_udf_query1)
        self.assertEqual(str(expected_stmt2), drop_udf_query2)

    def test_single_statement_queries(self):
        parser = Parser()

        single_queries = []
        single_queries.append("SELECT CLASS FROM TAIPAI;")
        single_queries.append("SELECT CLASS FROM TAIPAI WHERE CLASS = 'VAN';")
        single_queries.append(
            "SELECT CLASS,REDNESS FROM TAIPAI \
            WHERE CLASS = 'VAN' AND REDNESS > 20;"
        )
        single_queries.append(
            "SELECT CLASS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;"
        )
        single_queries.append(
            "SELECT CLASS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;"
        )

        for query in single_queries:
            eva_statement_list = parser.parse(query)

            self.assertIsInstance(eva_statement_list, list)
            self.assertEqual(len(eva_statement_list), 1)
            self.assertIsInstance(eva_statement_list[0], AbstractStatement)

    def test_multiple_statement_queries(self):
        parser = Parser()

        multiple_queries = []
        multiple_queries.append(
            "SELECT CLASS FROM TAIPAI \
                WHERE CLASS = 'VAN' AND REDNESS < 300  OR REDNESS > 500; \
                SELECT REDNESS FROM TAIPAI \
                WHERE (CLASS = 'VAN' AND REDNESS = 300)"
        )

        for query in multiple_queries:
            eva_statement_list = parser.parse(query)
            self.assertIsInstance(eva_statement_list, list)
            self.assertEqual(len(eva_statement_list), 2)
            self.assertIsInstance(eva_statement_list[0], AbstractStatement)
            self.assertIsInstance(eva_statement_list[1], AbstractStatement)

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
        self.assertEqual(select_stmt.target_list[0].etype, ExpressionType.TUPLE_VALUE)
        self.assertEqual(select_stmt.target_list[1].etype, ExpressionType.TUPLE_VALUE)

        # from_table
        self.assertIsNotNone(select_stmt.from_table)
        self.assertIsInstance(select_stmt.from_table, TableRef)
        self.assertEqual(select_stmt.from_table.table.table_name, "TAIPAI")

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
        """Testing setting different clauses for Select
        Statement class
        Class: SelectStatement"""

        select_stmt_new = SelectStatement()
        parser = Parser()

        select_query_new = "SELECT CLASS, REDNESS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 400 ) OR REDNESS > 700;"
        eva_statement_list = parser.parse(select_query_new)
        select_stmt = eva_statement_list[0]

        select_stmt_new.where_clause = select_stmt.where_clause
        select_stmt_new.target_list = select_stmt.target_list
        select_stmt_new.from_table = select_stmt.from_table

        self.assertEqual(select_stmt_new.where_clause, select_stmt.where_clause)
        self.assertEqual(select_stmt_new.target_list, select_stmt.target_list)
        self.assertEqual(select_stmt_new.from_table, select_stmt.from_table)
        self.assertEqual(str(select_stmt_new), str(select_stmt))

    def test_select_statement_groupby_class(self):
        """Testing sample frequency"""

        parser = Parser()

        select_query = "SELECT FIRST(id) FROM TAIPAI GROUP BY '8f';"

        eva_statement_list = parser.parse(select_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.SELECT)

        select_stmt = eva_statement_list[0]

        # target List
        self.assertIsNotNone(select_stmt.target_list)
        self.assertEqual(len(select_stmt.target_list), 1)
        self.assertEqual(
            select_stmt.target_list[0].etype, ExpressionType.AGGREGATION_FIRST
        )

        # from_table
        self.assertIsNotNone(select_stmt.from_table)
        self.assertIsInstance(select_stmt.from_table, TableRef)
        self.assertEqual(select_stmt.from_table.table.table_name, "TAIPAI")

        # sample_freq
        self.assertEqual(
            select_stmt.groupby_clause,
            ConstantValueExpression("8f", v_type=ColumnType.TEXT),
        )

    def test_select_statement_groupby_class_with_multiple_attributes_should_raise(self):
        # GROUP BY with multiple attributes should raise Syntax Error
        parser = Parser()
        select_query = "SELECT FIRST(id) FROM TAIPAI GROUP BY '8f', '12f';"
        self.assertRaises(SyntaxError, parser.parse, select_query)

    def test_select_statement_orderby_class(self):
        """Testing order by clause in select statement
        Class: SelectStatement"""

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
        self.assertEqual(select_stmt.target_list[0].etype, ExpressionType.TUPLE_VALUE)
        self.assertEqual(select_stmt.target_list[1].etype, ExpressionType.TUPLE_VALUE)

        # from_table
        self.assertIsNotNone(select_stmt.from_table)
        self.assertIsInstance(select_stmt.from_table, TableRef)
        self.assertEqual(select_stmt.from_table.table.table_name, "TAIPAI")

        # where_clause
        self.assertIsNotNone(select_stmt.where_clause)

        # orderby_clause
        self.assertIsNotNone(select_stmt.orderby_list)
        self.assertEqual(len(select_stmt.orderby_list), 2)
        self.assertEqual(select_stmt.orderby_list[0][0].col_name, "CLASS")
        self.assertEqual(select_stmt.orderby_list[0][1], ParserOrderBySortType.ASC)
        self.assertEqual(select_stmt.orderby_list[1][0].col_name, "REDNESS")
        self.assertEqual(select_stmt.orderby_list[1][1], ParserOrderBySortType.DESC)

    def test_select_statement_limit_class(self):
        """Testing limit clause in select statement
        Class: SelectStatement"""

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
        self.assertEqual(select_stmt.target_list[0].etype, ExpressionType.TUPLE_VALUE)
        self.assertEqual(select_stmt.target_list[1].etype, ExpressionType.TUPLE_VALUE)

        # from_table
        self.assertIsNotNone(select_stmt.from_table)
        self.assertIsInstance(select_stmt.from_table, TableRef)
        self.assertEqual(select_stmt.from_table.table.table_name, "TAIPAI")

        # where_clause
        self.assertIsNotNone(select_stmt.where_clause)

        # orderby_clause
        self.assertIsNotNone(select_stmt.orderby_list)
        self.assertEqual(len(select_stmt.orderby_list), 2)
        self.assertEqual(select_stmt.orderby_list[0][0].col_name, "CLASS")
        self.assertEqual(select_stmt.orderby_list[0][1], ParserOrderBySortType.ASC)
        self.assertEqual(select_stmt.orderby_list[1][0].col_name, "REDNESS")
        self.assertEqual(select_stmt.orderby_list[1][1], ParserOrderBySortType.DESC)

        # limit_count
        self.assertIsNotNone(select_stmt.limit_count)
        self.assertEqual(select_stmt.limit_count, ConstantValueExpression(3))

    def test_select_statement_sample_class(self):
        """Testing sample frequency"""

        parser = Parser()

        select_query = "SELECT CLASS, REDNESS FROM TAIPAI SAMPLE 5;"

        eva_statement_list = parser.parse(select_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.SELECT)

        select_stmt = eva_statement_list[0]

        # target List
        self.assertIsNotNone(select_stmt.target_list)
        self.assertEqual(len(select_stmt.target_list), 2)
        self.assertEqual(select_stmt.target_list[0].etype, ExpressionType.TUPLE_VALUE)
        self.assertEqual(select_stmt.target_list[1].etype, ExpressionType.TUPLE_VALUE)

        # from_table
        self.assertIsNotNone(select_stmt.from_table)
        self.assertIsInstance(select_stmt.from_table, TableRef)
        self.assertEqual(select_stmt.from_table.table.table_name, "TAIPAI")

        # sample_freq
        self.assertEqual(select_stmt.from_table.sample_freq, ConstantValueExpression(5))

    def test_table_ref(self):
        """Testing table info in TableRef
        Class: TableInfo
        """
        table_info = TableInfo("TAIPAI", "Schema", "Database")
        table_ref_obj = TableRef(table_info)
        select_stmt_new = SelectStatement()
        select_stmt_new.from_table = table_ref_obj
        self.assertEqual(select_stmt_new.from_table.table.table_name, "TAIPAI")
        self.assertEqual(select_stmt_new.from_table.table.schema_name, "Schema")
        self.assertEqual(select_stmt_new.from_table.table.database_name, "Database")

    def test_insert_statement(self):
        parser = Parser()
        insert_query = """INSERT INTO MyVideo (Frame_ID, Frame_Path)
                                    VALUES    (1, '/mnt/frames/1.png');
                        """
        expected_stmt = InsertTableStatement(
            TableRef(TableInfo("MyVideo")),
            [
                TupleValueExpression("Frame_ID"),
                TupleValueExpression("Frame_Path"),
            ],
            [
                ConstantValueExpression(1),
                ConstantValueExpression("/mnt/frames/1.png", ColumnType.TEXT),
            ],
        )
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

        expected_cci = ColConstraintInfo()
        expected_cci.nullable = True
        expected_stmt = CreateUDFStatement(
            "FastRCNN",
            False,
            [
                ColumnDefinition(
                    "Frame_Array",
                    ColumnType.NDARRAY,
                    NdArrayType.UINT8,
                    [3, 256, 256],
                    expected_cci,
                )
            ],
            [
                ColumnDefinition(
                    "Labels", ColumnType.NDARRAY, NdArrayType.STR, [10], expected_cci
                ),
                ColumnDefinition(
                    "Bbox", ColumnType.NDARRAY, NdArrayType.UINT8, [10, 4], expected_cci
                ),
            ],
            Path("data/fastrcnn.py"),
            "Classification",
        )
        eva_statement_list = parser.parse(create_udf_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.CREATE_UDF)

        create_udf_stmt = eva_statement_list[0]

        self.assertEqual(create_udf_stmt, expected_stmt)

    def test_load_video_data_statement(self):
        parser = Parser()
        load_data_query = """LOAD FILE 'data/video.mp4'
                             INTO MyVideo WITH FORMAT VIDEO;"""
        file_options = {}
        file_options["file_format"] = FileFormatType.VIDEO
        column_list = None
        expected_stmt = LoadDataStatement(
            TableRef(TableInfo("MyVideo")),
            Path("data/video.mp4"),
            column_list,
            file_options,
        )
        eva_statement_list = parser.parse(load_data_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.LOAD_DATA)

        load_data_stmt = eva_statement_list[0]
        self.assertEqual(load_data_stmt, expected_stmt)

    def test_load_csv_data_statement(self):
        parser = Parser()
        load_data_query = """LOAD FILE 'data/meta.csv'
                             INTO
                             MyMeta (id, frame_id, video_id, label)
                             WITH FORMAT CSV;"""
        file_options = {}
        file_options["file_format"] = FileFormatType.CSV
        expected_stmt = LoadDataStatement(
            TableRef(TableInfo("MyMeta")),
            Path("data/meta.csv"),
            [
                TupleValueExpression("id"),
                TupleValueExpression("frame_id"),
                TupleValueExpression("video_id"),
                TupleValueExpression("label"),
            ],
            file_options,
        )
        eva_statement_list = parser.parse(load_data_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.LOAD_DATA)

        load_data_stmt = eva_statement_list[0]
        self.assertEqual(load_data_stmt, expected_stmt)

    def test_upload_statement(self):
        parser = Parser()
        upload_query = """UPLOAD PATH 'data/video.mp4' BLOB "b'AAAA'"
                          INTO MyVideo WITH FORMAT VIDEO;"""

        file_options = {}
        file_options["file_format"] = FileFormatType.VIDEO
        column_list = None

        expected_stmt = UploadStatement(
            Path("data/video.mp4"),
            "b'AAAA'",
            TableRef(TableInfo("MyVideo")),
            column_list,
            file_options,
        )

        eva_statement_list = parser.parse(upload_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.UPLOAD)

        upload_stmt = eva_statement_list[0]
        self.assertEqual(upload_stmt, expected_stmt)

    def test_upload_csv_data_statement(self):
        parser = Parser()

        upload_query = """UPLOAD PATH 'data/meta.csv' BLOB "b'AAAA'"
                          INTO
                          MyMeta (id, frame_id, video_id, label)
                          WITH FORMAT CSV;"""

        file_options = {}
        file_options["file_format"] = FileFormatType.CSV
        expected_stmt = UploadStatement(
            Path("data/meta.csv"),
            "b'AAAA'",
            TableRef(TableInfo("MyMeta")),
            [
                TupleValueExpression("id"),
                TupleValueExpression("frame_id"),
                TupleValueExpression("video_id"),
                TupleValueExpression("label"),
            ],
            file_options,
        )
        eva_statement_list = parser.parse(upload_query)
        self.assertIsInstance(eva_statement_list, list)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list[0].stmt_type, StatementType.UPLOAD)

        upload_stmt = eva_statement_list[0]
        self.assertEqual(upload_stmt, expected_stmt)

    def test_nested_select_statement(self):
        parser = Parser()
        sub_query = """SELECT CLASS FROM TAIPAI WHERE CLASS = 'VAN'"""
        nested_query = """SELECT ID FROM ({}) AS T;""".format(sub_query)
        parsed_sub_query = parser.parse(sub_query)[0]
        actual_stmt = parser.parse(nested_query)[0]
        self.assertEqual(actual_stmt.stmt_type, StatementType.SELECT)
        self.assertEqual(actual_stmt.target_list[0].col_name, "ID")
        self.assertEqual(
            actual_stmt.from_table, TableRef(parsed_sub_query, alias=Alias("T"))
        )

        sub_query = """SELECT Yolo(frame).bbox FROM autonomous_vehicle_1
                              WHERE Yolo(frame).label = 'vehicle'"""
        nested_query = """SELECT Licence_plate(bbox) FROM
                            ({}) AS T
                          WHERE Is_suspicious(bbox) = 1 AND
                                Licence_plate(bbox) = '12345';
                      """.format(
            sub_query
        )
        query = """SELECT Licence_plate(bbox) FROM TAIPAI
                    WHERE Is_suspicious(bbox) = 1 AND
                        Licence_plate(bbox) = '12345';
                """
        query_stmt = parser.parse(query)[0]
        actual_stmt = parser.parse(nested_query)[0]
        sub_query_stmt = parser.parse(sub_query)[0]
        self.assertEqual(
            actual_stmt.from_table, TableRef(sub_query_stmt, alias=Alias("T"))
        )
        self.assertEqual(actual_stmt.where_clause, query_stmt.where_clause)
        self.assertEqual(actual_stmt.target_list, query_stmt.target_list)

    def test_should_return_false_for_unequal_expression(self):
        table = TableRef(TableInfo("MyVideo"))
        load_stmt = LoadDataStatement(
            table, Path("data/video.mp4"), FileFormatType.VIDEO
        )
        insert_stmt = InsertTableStatement(table)
        create_udf = CreateUDFStatement(
            "udf",
            False,
            [
                ColumnDefinition(
                    "frame",
                    ColumnType.NDARRAY,
                    NdArrayType.UINT8,
                    [3, 256, 256],
                )
            ],
            [ColumnDefinition("labels", ColumnType.NDARRAY, NdArrayType.STR, [10])],
            Path("data/fastrcnn.py"),
            "Classification",
        )
        select_stmt = SelectStatement()
        self.assertNotEqual(load_stmt, insert_stmt)
        self.assertNotEqual(insert_stmt, load_stmt)
        self.assertNotEqual(create_udf, insert_stmt)
        self.assertNotEqual(select_stmt, create_udf)

    def test_materialized_view(self):
        select_query = """SELECT id, FastRCNNObjectDetector(frame).labels FROM MyVideo
                        WHERE id<5; """
        query = "CREATE MATERIALIZED VIEW uadtrac_fastRCNN (id, labels) AS {}".format(
            select_query
        )
        parser = Parser()
        mat_view_stmt = parser.parse(query)
        select_stmt = parser.parse(select_query)
        expected_stmt = CreateMaterializedViewStatement(
            TableRef(TableInfo("uadtrac_fastRCNN")),
            [
                ColumnDefinition("id", None, None, None),
                ColumnDefinition("labels", None, None, None),
            ],
            False,
            select_stmt[0],
        )
        self.assertEqual(mat_view_stmt[0], expected_stmt)

    def test_join(self):
        select_query = """SELECT table1.a FROM table1 JOIN table2
                    ON table1.a = table2.a; """
        parser = Parser()
        select_stmt = parser.parse(select_query)[0]
        table1_col_a = TupleValueExpression("a", "table1")
        table2_col_a = TupleValueExpression("a", "table2")
        select_list = [table1_col_a]
        from_table = TableRef(
            JoinNode(
                TableRef(TableInfo("table1")),
                TableRef(TableInfo("table2")),
                predicate=ComparisonExpression(
                    ExpressionType.COMPARE_EQUAL, table1_col_a, table2_col_a
                ),
                join_type=JoinType.INNER_JOIN,
            )
        )
        expected_stmt = SelectStatement(select_list, from_table)

        self.assertEqual(select_stmt, expected_stmt)

    def test_join_with_where(self):
        select_query = """SELECT table1.a FROM table1 JOIN table2
            ON table1.a = table2.a WHERE table1.a <= 5"""
        parser = Parser()
        select_stmt = parser.parse(select_query)[0]
        table1_col_a = TupleValueExpression("a", "table1")
        table2_col_a = TupleValueExpression("a", "table2")
        select_list = [table1_col_a]
        from_table = TableRef(
            JoinNode(
                TableRef(TableInfo("table1")),
                TableRef(TableInfo("table2")),
                predicate=ComparisonExpression(
                    ExpressionType.COMPARE_EQUAL, table1_col_a, table2_col_a
                ),
                join_type=JoinType.INNER_JOIN,
            )
        )
        where_clause = ComparisonExpression(
            ExpressionType.COMPARE_LEQ,
            table1_col_a,
            ConstantValueExpression(5),
        )
        expected_stmt = SelectStatement(select_list, from_table, where_clause)
        self.assertEqual(select_stmt, expected_stmt)

    def test_multiple_join_with_multiple_ON(self):
        select_query = """SELECT table1.a FROM table1 JOIN table2
            ON table1.a = table2.a JOIN table3
            ON table3.a = table1.a WHERE table1.a <= 5"""
        parser = Parser()
        select_stmt = parser.parse(select_query)[0]
        table1_col_a = TupleValueExpression("a", "table1")
        table2_col_a = TupleValueExpression("a", "table2")
        table3_col_a = TupleValueExpression("a", "table3")
        select_list = [table1_col_a]
        child_join = TableRef(
            JoinNode(
                TableRef(TableInfo("table1")),
                TableRef(TableInfo("table2")),
                predicate=ComparisonExpression(
                    ExpressionType.COMPARE_EQUAL, table1_col_a, table2_col_a
                ),
                join_type=JoinType.INNER_JOIN,
            )
        )

        from_table = TableRef(
            JoinNode(
                child_join,
                TableRef(TableInfo("table3")),
                predicate=ComparisonExpression(
                    ExpressionType.COMPARE_EQUAL, table3_col_a, table1_col_a
                ),
                join_type=JoinType.INNER_JOIN,
            )
        )
        where_clause = ComparisonExpression(
            ExpressionType.COMPARE_LEQ,
            table1_col_a,
            ConstantValueExpression(5),
        )
        expected_stmt = SelectStatement(select_list, from_table, where_clause)
        self.assertEqual(select_stmt, expected_stmt)

    def test_multiple_join_with_single_ON_should_raise(self):
        select_query = """SELECT table1.a FROM table1 JOIN table2 JOIN table3
                    ON table3.a = table1.a AND table1.a = table2.a;"""
        parser = Parser()
        with self.assertRaises(Exception):
            parser.parse(select_query)[0]

    def test_lateral_join(self):
        select_query = """SELECT frame FROM MyVideo JOIN LATERAL
                            ObjectDet(frame) AS OD;"""
        parser = Parser()
        select_stmt = parser.parse(select_query)[0]
        tuple_frame = TupleValueExpression("frame")
        func_expr = FunctionExpression(
            func=None, name="ObjectDet", children=[tuple_frame]
        )
        from_table = TableRef(
            JoinNode(
                TableRef(TableInfo("MyVideo")),
                TableRef(TableValuedExpression(func_expr), alias=Alias("OD")),
                join_type=JoinType.LATERAL_JOIN,
            )
        )
        expected_stmt = SelectStatement([tuple_frame], from_table)
        self.assertEqual(select_stmt, expected_stmt)
