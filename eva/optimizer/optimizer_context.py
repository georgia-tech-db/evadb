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
        opr: Operator
    ) -> GroupExpression:
        """
        Generate a group expressions from a logical operator tree.
        """
        # Go through the children first.
        child_ids = []
        for child_opr in opr.children:
            child_expr = self.xform_opr_to_group_expr(opr=child_opr)
            child_ids.append(child_expr.group_id)

        expr = GroupExpression(opr=opr, children=child_ids)
        # add the expr to memo
        # handles duplicates and assigns group id    
        memo_expr = self.memo.add_group_expr(expr)
        return memo_expr
    
    def replace_expression(self, opr: Operator, group_id: int):
        """ 
        Removes all the expressions from the group and adds the new expression
        This is called by rewrite rules
        """
        self.memo.erase_group(group_id)
        new_expr = self.xform_opr_to_group_expr(opr)
        self.memo.add_group_expr(new_expr)

