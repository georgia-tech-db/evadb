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

import copy
import itertools

from src.optimizer.rules.pattern import Pattern
from src.optimizer.group_expression import GroupExpression
from src.optimizer.memo import Memo
from src.optimizer.operators import Operator, OperatorType


class Binder:
    def __init__(self, grp_expr: GroupExpression, pattern: Pattern, memo: Memo):
        self._grp_expr = grp_expr
        self._pattern = pattern
        self._memo = memo

    @staticmethod
    def _grp_binder(id: int, pattern: Pattern, memo: Memo):
        grp = memo.get_group(id)
        grp_exprs = grp.logical_exprs

        for expr in grp.logical_exprs:
            yield from Binder._binder(expr, pattern, memo)

    @staticmethod
    def _binder(expr: GroupExpression, pattern: Pattern, memo: Memo):
        curr_iterator = iter([expr.opr])
        child_binders = []
        if pattern.opr_type is not OperatorType.DUMMY:
            if expr.opr.opr_type != pattern.opr_type:
                return

            if len(pattern.children) != len(expr.children):
                return

            for child_grp, pattern_child in zip(expr.children,
                                                pattern.children):
                child_binders.append(
                    Binder._grp_binder(child_grp, pattern_child, memo)
                )

        yield from itertools.product(curr_iterator, *child_binders)

    @staticmethod
    def build_opr_tree_from_inorder_repr(inorder_repr: tuple) -> Operator:
        if isinstance(inorder_repr, Operator):
            return inorder_repr
        else:
            opr_tree = inorder_repr[0]
            if len(inorder_repr) > 1:
                # remove old children
                opr_tree.children.clear()
                for child in inorder_repr[1:]:
                    opr_tree.append_child(Binder.build_opr_tree_from_inorder_repr(child))
            return opr_tree

    def __iter__(self):
        for match in Binder._binder(self._grp_expr, self._pattern, self._memo):
            yield Binder.build_opr_tree_from_inorder_repr(match)

