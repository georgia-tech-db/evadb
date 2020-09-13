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
from src.optimizer.operators import Operator


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
            yield from _binder(expr, pattern, memo)

    @staticmethod
    def _binder(expr: GroupExpression, pattern: Pattern, memo: Memo):
        if expr.opr.type != pattern.opr_type:
            return

        if not len(pattern.children):
            yield expr.opr

        if len(pattern.children) != len(expr.opr.children):
            return

        child_binders = []
        for expr_child, pattern_child in zip(expr.opr.children, pattern.children):
            child_binders.append(_grp_binder(expr_child, pattern_child, memo))
        
        yield from itertools.product(*child_binders)

    @staticmethod
    def build_opr_tree_from_inorder_repr(inorder_repr: tuple) -> Operator:
        if isinstance(inorder_repr, Operator):
            return inorder_repr
        else:
            opr_tree = inorder_repr[0]
            for child in inorder_repr[1:]:
                opr_tree.append_child(build_opr_tree_from_inorder_repr(child))
            return opr_tree
            
    def __iter__(self):
        for match in _binder(self._grp_expr, self._pattern, self._memo):
            yield Binder.build_opr_tree_from_inorder_repr(match)
            