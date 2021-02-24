import unittest

from mock import MagicMock

from src.optimizer.operators import LogicalGet, LogicalFilter
from src.optimizer.rules.rules import EmbedFilterIntoGet


class TestEmbedFilterIntoGet(unittest.TestCase):
    def test_simple_filter_into_get(self):
        rule = EmbedFilterIntoGet()
        predicate = MagicMock()

        logi_get = LogicalGet(MagicMock(), MagicMock())
        logi_filter = LogicalFilter(predicate, [logi_get])

        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertEqual(rewrite_opr, logi_get)
        self.assertEqual(rewrite_opr.predicate, predicate)
