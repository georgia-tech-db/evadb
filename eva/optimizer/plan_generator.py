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
from eva.optimizer.cost_model import CostModel
from eva.optimizer.operators import Operator
from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.optimizer_task_stack import OptimizerTaskStack
from eva.optimizer.optimizer_tasks import BottomUpRewrite, OptimizeGroup, TopDownRewrite
from eva.optimizer.property import PropertyType
from eva.optimizer.rules.rules_manager import RulesManager


class PlanGenerator:
    """
    Used for building Physical Plan from Logical Plan.
    """

    def __init__(
        self, rules_manager: RulesManager = None, cost_model: CostModel = None
    ) -> None:
        self.rules_manager = rules_manager or RulesManager()
        self.cost_model = cost_model or CostModel()

    def execute_task_stack(self, task_stack: OptimizerTaskStack):
        while not task_stack.empty():
            task = task_stack.pop()
            task.execute()

    def build_optimal_physical_plan(
        self, root_grp_id: int, optimizer_context: OptimizerContext
    ):
        physical_plan = None
        root_grp = optimizer_context.memo.groups[root_grp_id]
        best_grp_expr = root_grp.get_best_expr(PropertyType.DEFAULT)
        physical_plan = best_grp_expr.opr

        for child_grp_id in best_grp_expr.children:
            child_plan = self.build_optimal_physical_plan(
                child_grp_id, optimizer_context
            )
            physical_plan.append_child(child_plan)

        return physical_plan

    def optimize(self, logical_plan: Operator):
        optimizer_context = OptimizerContext(self.cost_model)
        memo = optimizer_context.memo
        grp_expr = optimizer_context.add_opr_to_group(opr=logical_plan)
        root_grp_id = grp_expr.group_id
        root_expr = memo.groups[root_grp_id].logical_exprs[0]

        # TopDown Rewrite
        optimizer_context.task_stack.push(
            TopDownRewrite(
                root_expr, self.rules_manager.rewrite_rules, optimizer_context
            )
        )
        self.execute_task_stack(optimizer_context.task_stack)

        # BottomUp Rewrite
        root_expr = memo.groups[root_grp_id].logical_exprs[0]
        optimizer_context.task_stack.push(
            BottomUpRewrite(
                root_expr, self.rules_manager.rewrite_rules, optimizer_context
            )
        )
        self.execute_task_stack(optimizer_context.task_stack)

        # Optimize Expression (logical -> physical transformation)
        root_group = memo.get_group_by_id(root_grp_id)
        optimizer_context.task_stack.push(OptimizeGroup(root_group, optimizer_context))
        self.execute_task_stack(optimizer_context.task_stack)

        # Build Optimal Tree
        optimal_plan = self.build_optimal_physical_plan(root_grp_id, optimizer_context)
        return optimal_plan

    def build(self, logical_plan: Operator):
        # apply optimizations

        plan = self.optimize(logical_plan)
        return plan
