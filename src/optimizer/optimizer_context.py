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
from src.optimizer.optimizer_task_queue import OptimizerTaskQueue
from src.optimizer.memo import Memo
from src.optimizer.operators import Operator
from src.optimizer.group_expression import GroupExpression


class OptimizerContext:
    """
        Maintain context information for the optimizer 

        Arguments:
            _optimizer_task_queue(OptimizerTaskQueue): 
                queue to keep track outstanding tasks 
    """

    def __init__(self):
        self._optimizer_task_queue = OptimizerTaskQueue()
        self._memo = Memo()

    @property
    def optimizer_task_queue(self):
        return self._optimizer_task_queue

    @property
    def memo(self):
        return self._memo

    def build_group_expr(self, expr: Operator) -> GroupExpression:
        grp_exp = None
        child_ids = [build_group_expr(
            child_opr).group_id for child_opr in expr.children]
        grp_exp = GroupExpression(children=child_ids)
        self.memo.insert_group_expr(grp_exp)
        
