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
from src.optimizer.optimizer_task_stack import OptimizerTaskStack
from src.optimizer.memo import Memo
from src.optimizer.operators import Operator
from src.optimizer.group_expression import GroupExpression


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

    def xform_opr_to_group_expr(self, opr: Operator, copy_opr=True) -> GroupExpression:
        grp_exp = None
        child_ids = []
        for child_opr in opr.children:
            child_id = self.xform_opr_to_group_expr(child_opr, copy_opr).group_id
            child_ids.append(child_id)
        if copy_opr:
            opr_copy = copy.deepcopy(opr)
            opr = opr_copy
        grp_exp = GroupExpression(opr=opr, children=child_ids)
        self.memo.add_group_expr(grp_exp)
        return grp_exp
