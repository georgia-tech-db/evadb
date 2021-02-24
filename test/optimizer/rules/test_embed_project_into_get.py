import unittest

from mock import MagicMock

from src.optimizer.operators import LogicalGet, LogicalProject
from src.optimizer.rules.rules import EmbedProjectIntoGet


class TestEmbedProjectIntoGet(unittest.TestCase):
    def test_simple_project_into_get(self):
        rule = EmbedProjectIntoGet()
        expr1 = MagicMock()
        expr2 = MagicMock()
        expr3 = MagicMock()

        logi_get = LogicalGet(MagicMock(), MagicMock())
        logi_project = LogicalProject([expr1, expr2, expr3], [logi_get])

        rewrite_opr = rule.apply(logi_project, MagicMock())
        self.assertEqual(rewrite_opr, logi_get)
        self.assertEqual(rewrite_opr.target_list, [expr1, expr2, expr3])
