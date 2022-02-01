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
from eva.optimizer.optimizer_task_stack import OptimizerTaskStack
from eva.optimizer.memo import Memo
from eva.optimizer.operators import Operator
from eva.optimizer.group_expression import GroupExpression
from eva.constants import INVALID_GROUP_ID


class OptimizerContext:
    """
        Maintain context information for the optimizer

        Arguments:
            _task_queue(OptimizerTaskStack):
                stack to keep track outstanding tasks
    """

    def __init__(self):
        self._task_stack = OptimizerTaskStack()
        self._memo = Memo()

    @property
    def task_stack(self):
        return self._task_stack

    @property
    def memo(self):
        return self._memo

    def xform_opr_to_group_expr(
        self,
        opr: Operator,
        root_group_id: int = INVALID_GROUP_ID,
        is_root: bool = False,
        copy_opr: bool = True
    ) -> GroupExpression:
        """
        Generate a group expression from a logical operator.
        If the root_group_id is given, then the group_id of the
        root logical operator is guaranteed.
        """

        # Go through the children first.
        child_ids = []
        for child_opr in opr.children:
            child_id = self.xform_opr_to_group_expr(
                opr=child_opr,
                root_group_id=root_group_id,
                is_root=False,
                copy_opr=copy_opr
            ).group_id
            child_ids.append(child_id)

        # Check if we need copy
        if copy_opr:
            opr_copy = copy.deepcopy(opr)
            opr = opr_copy

        if is_root:
            expr = GroupExpression(opr=opr, group_id=root_group_id,
                                   children=child_ids)
            expr = self.memo.add_group_expr(expr)
            assert root_group_id == INVALID_GROUP_ID or \
                expr.group_id == root_group_id
        else:
            # If not root, we do not care the group_id
            expr = GroupExpression(opr=opr, group_id=INVALID_GROUP_ID,
                                   children=child_ids)
            expr = self.memo.add_group_expr(expr)
            if root_group_id != INVALID_GROUP_ID and \
                    expr.group_id == root_group_id:
                # This expr has the same group_id with the root one,
                # so we need give it a new group.
                self.memo._remove_expr(expr)
                self.memo._append_expr(expr)
            assert root_group_id == INVALID_GROUP_ID or \
                expr.group_id != root_group_id

        return expr
