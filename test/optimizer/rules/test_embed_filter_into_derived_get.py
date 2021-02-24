import unittest

from mock import MagicMock

from src.optimizer.operators import (
    LogicalQueryDerivedGet, LogicalFilter, Dummy)
from src.optimizer.rules.rules import EmbedFilterIntoDerivedGet


class TestEmbedFilterIntoDerivedGet(unittest.TestCase):
    def test_simple_filter_into_derived_get(self):
        rule = EmbedFilterIntoDerivedGet()
        predicate = MagicMock()

        logi_derived_get = LogicalQueryDerivedGet([Dummy()])
        logi_filter = LogicalFilter(predicate, [logi_derived_get])

        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertEqual(rewrite_opr, logi_derived_get)
        self.assertEqual(rewrite_opr.predicate, predicate)
