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

from eva.constants import UNDEFINED_GROUP_ID
from eva.optimizer.cost_model import CostModel
from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.memo import Memo
from eva.optimizer.operators import Dummy, Operator
from eva.optimizer.optimizer_task_stack import OptimizerTaskStack


class OptimizerContext:
    """
    Maintain context information for the optimizer

    Arguments:
        _task_queue(OptimizerTaskStack):
            stack to keep track outstanding tasks
    """

    def __init__(self, cost_model: CostModel):
        self._task_stack = OptimizerTaskStack()
        self._memo = Memo()
        self._cost_model = cost_model

    @property
    def cost_model(self):
        return self._cost_model

    @property
    def task_stack(self):
        return self._task_stack

    @property
    def memo(self):
        return self._memo

    def _xform_opr_to_group_expr(self, opr: Operator) -> GroupExpression:
        """
        Note: Internal function Generate a group expressions from a
        logical operator tree. Caller is responsible for assigning
        the group to the returned GroupExpression.
        """
        # Go through the children first.
        child_ids = []
        for child_opr in opr.children:
            if isinstance(child_opr, Dummy):
                child_ids.append(child_opr.group_id)
            else:
                child_expr = self._xform_opr_to_group_expr(opr=child_opr)
                # add the expr to memo
                # handles duplicates and assigns group id
                memo_expr = self.memo.add_group_expr(child_expr)
                child_ids.append(memo_expr.group_id)

        # Group Expression only needs the operator content. Remove
        # the opr children as parent-child relationship is captured
        # by the group expressions.
        # Hack: Shallow copy all the content except children and
        # manually clearing the children as we don't need the
        # dependency. Better fix is to rewrite the operator class to
        # support  exposing only the content
        opr_copy = copy.copy(opr)
        opr_copy.clear_children()
        expr = GroupExpression(opr=opr_copy, children=child_ids)
        return expr

    def replace_expression(self, opr: Operator, group_id: int):
        """
        Removes all the expressions from the specified group and
        create a new expression. This is called by rewrite rules. The
        new expr gets assigned a new group id
        """
        self.memo.erase_group(group_id)
        new_expr = self._xform_opr_to_group_expr(opr)
        new_expr = self.memo.add_group_expr(new_expr, group_id)
        return new_expr

    def add_opr_to_group(self, opr: Operator, group_id: int = UNDEFINED_GROUP_ID):
        """
        Convert opertator to group_expression and add to the group
        """
        grp_expr = self._xform_opr_to_group_expr(opr)
        grp_expr = self.memo.add_group_expr(grp_expr, group_id)
        return grp_expr
