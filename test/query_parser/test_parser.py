import unittest
from src.query_parser.eva_parser import EvaFrameQLParser
from src.query_parser.eva_statement import EvaStatementList, EvaStatement
from src.query_parser.eva_statement import StatementType
from src.query_parser.select_statement import SelectStatement
from src.expression.abstract_expression import ExpressionType


class ParserTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_eva_parser(self):
        eva = EvaFrameQLParser()
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
            eva_statement_list = eva.build_eva_parse_tree(query)
            self.assertIsInstance(eva_statement_list, EvaStatementList)
            self.assertEqual(len(eva_statement_list), 1)
            self.assertIsInstance(
                eva_statement_list.get_statement(0), EvaStatement)

        multiple_queries = []
        multiple_queries.append("SELECT CLASS FROM TAIPAI \
            WHERE CLASS = 'VAN' AND REDNESS < 300  OR REDNESS > 500; \
            SELECT REDNESS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS = 300)")

        for query in multiple_queries:
            eva_statement_list = eva.build_eva_parse_tree(query)
            self.assertIsInstance(eva_statement_list, EvaStatementList)
            self.assertEqual(len(eva_statement_list), 2)
            self.assertIsInstance(
                eva_statement_list.get_statement(0), EvaStatement)
            self.assertIsInstance(
                eva_statement_list.get_statement(1), EvaStatement)

    def test_select_parser(self):
        eva = EvaFrameQLParser()
        select_query = "SELECT CLASS, REDNESS FROM TAIPAI \
            WHERE (CLASS = 'VAN' AND REDNESS < 300 ) OR REDNESS > 500;"
        eva_statement_list = eva.build_eva_parse_tree(select_query)
        self.assertIsInstance(eva_statement_list, EvaStatementList)
        self.assertEqual(len(eva_statement_list), 1)
        self.assertEqual(eva_statement_list.get_statement(
            0).stmt_type, StatementType.SELECT)

        select_stmt = eva_statement_list.get_statement(0)

        # target List
        self.assertIsNotNone(select_stmt.target_list)
        self.assertEqual(len(select_stmt.target_list), 2)
        self.assertEqual(
            select_stmt.target_list[0].etype, ExpressionType.TUPLE_VALUE)
        self.assertEqual(
            select_stmt.target_list[1].etype, ExpressionType.TUPLE_VALUE)

        # from_table
        # Todo change this to table ref
        self.assertIsNotNone(select_stmt.from_table)
        # self.assertEqual(select_stmt.from_table.etype,
        #   ExpressionType.TUPLE_VALUE)

        # where_clause
        self.assertIsNotNone(select_stmt.where_clause)
        # other tests should go in expression testing


if __name__ == '__main__':
    unittest.main()
