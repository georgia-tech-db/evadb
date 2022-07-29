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
import copy
import itertools

from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.memo import Memo
from eva.optimizer.operators import Dummy, Operator, OperatorType
from eva.optimizer.rules.pattern import Pattern


class Binder:
    def __init__(self, grp_expr: GroupExpression, pattern: Pattern, memo: Memo):
        self._grp_expr = grp_expr
        self._pattern = pattern
        self._memo = memo

    @staticmethod
    def _grp_binder(idx: int, pattern: Pattern, memo: Memo):
        grp = memo.groups[idx]

        for expr in grp.logical_exprs:
            yield from Binder._binder(expr, pattern, memo)

    @staticmethod
    def _binder(expr: GroupExpression, pattern: Pattern, memo: Memo):
        assert isinstance(expr, GroupExpression)
        curr_iterator = iter(())
        child_binders = []
        if pattern.opr_type is not OperatorType.DUMMY:
            curr_iterator = iter([expr.opr])
            if expr.opr.opr_type != pattern.opr_type:
                return

            if len(pattern.children) != len(expr.children):
                return

            for child_grp, pattern_child in zip(expr.children, pattern.children):
                child_binders.append(Binder._grp_binder(child_grp, pattern_child, memo))
        else:
            # record the group id in a Dummy Opearator
            curr_iterator = iter([Dummy(expr.group_id)])

        yield from itertools.product(curr_iterator, *child_binders)

    @staticmethod
    def build_opr_tree_from_pre_order_repr(pre_order_repr: tuple) -> Operator:
        if isinstance(pre_order_repr, Operator):
            return pre_order_repr
        else:
            opr_tree = pre_order_repr[0]
            opr_tree.children.clear()
            if len(pre_order_repr) > 1:
                # remove old children
                for child in pre_order_repr[1:]:
                    opr_tree.append_child(
                        Binder.build_opr_tree_from_pre_order_repr(child)
                    )
            return opr_tree

    def __iter__(self):
        # the iterator only returns one match, which stems from the root node
        for match in Binder._binder(self._grp_expr, self._pattern, self._memo):
            # We should not modify the operator in the group
            # expression as it might be used in later rules. Hack:
            # Creating a copy of the match Potential fix: Store only
            # the content in the group expression and manage the
            # parent-child relationship separately. Refer
            # optimizer_context:_xform_opr_to_group_expr
            match_copy = [copy.copy(opr) for opr in match]
            x = Binder.build_opr_tree_from_pre_order_repr(match_copy)
            yield x
