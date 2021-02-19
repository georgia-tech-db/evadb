import unittest

from mock import MagicMock

from src.optimizer.memo import Memo
from src.optimizer.group import INVALID_GROUP_ID


class MemoTest(unittest.TestCase):
    def test_memo_add_with_no_forcing_id(self):
        group_expr = MagicMock()
        group_expr.group_id = INVALID_GROUP_ID
        memo = Memo()
        self.assertEqual(memo.add_group_expr(group_expr), group_expr)

    def test_memo_add_with_forcing_id(self):
        group_expr = MagicMock()
        group_expr.group_id = 0
        memo = Memo()
        self.assertEqual(memo.add_group_expr(group_expr), group_expr)

    def test_memo_add_existing_group_id_under_no_forcing_id(self):
        group_expr = MagicMock()
        group_expr.group_id = INVALID_GROUP_ID

        memo = Memo()
        memo.add_group_expr(group_expr)
        ret_expr = memo.add_group_expr(group_expr)
        self.assertEqual(ret_expr, group_expr)
        self.assertEqual(len(memo.group_exprs), 1)

    def test_memo_add_existing_group_id_under_forcing_id(self):
        group_expr1 = MagicMock()
        group_expr1.group_id = INVALID_GROUP_ID
        group_expr2 = MagicMock()
        group_expr2.group_id = 0

        memo = Memo()
        memo.add_group_expr(group_expr1)
        ret_expr = memo.add_group_expr(group_expr2)
        self.assertEqual(ret_expr.group_id, 0)
        self.assertEqual(len(memo.groups), 1)
        self.assertEqual(len(memo.group_exprs), 1)
