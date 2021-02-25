import unittest

from mock import MagicMock

from src.catalog.catalog_manager import CatalogManager
from src.optimizer.rules.rules import LogicalUdfFilterToPhysical
from src.optimizer.operators import LogicalFilter, Dummy
from src.expression.abstract_expression import ExpressionType
from src.server.command_handler import execute_query_fetch_all
from src.catalog.column_type import ColumnType

from test.util import DummyObjectDetector


class TestLogicalUdfFilterToPhysical(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()

    def test_logical_udf_filter_to_physical(self):
        rule = LogicalUdfFilterToPhysical()

        expr1 = MagicMock()
        expr1.etype = ExpressionType.FUNCTION_EXPRESSION
        expr1.name = "Classification"
        expr1.output = "label"
        expr1.is_logical = lambda: True

        expr2 = MagicMock()
        expr2.etype = ExpressionType.FUNCTION_EXPRESSION
        expr2.name = "Classification"
        expr2.output = "label"
        expr2.is_logical = lambda: True

        expr1.children = [expr2]

        # create udf in catalog manager
        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (label TEXT(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        execute_query_fetch_all(create_udf_query)

        logi_filter = LogicalFilter(expr1)
        rule.apply(logi_filter, MagicMock())

        self.assertEqual(expr1.function.name, DummyObjectDetector().name)
        self.assertEqual(expr1.output_obj.type, ColumnType.TEXT)
        self.assertEqual(expr2.function.name, DummyObjectDetector().name)
        self.assertEqual(expr2.output_obj.type, ColumnType.TEXT)
