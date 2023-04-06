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
from eva.configuration.configuration_manager import ConfigurationManager
from eva.experimental.ray.planner.exchange_plan import ExchangePlan
from eva.optimizer.cost_model import CostModel
from eva.optimizer.operators import Operator
from eva.optimizer.optimizer_context import OptimizerContext
from eva.optimizer.optimizer_task_stack import OptimizerTaskStack
from eva.optimizer.optimizer_tasks import BottomUpRewrite, OptimizeGroup, TopDownRewrite
from eva.optimizer.property import PropertyType
from eva.optimizer.rules.rules_manager import RulesManager
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.plan_nodes.create_mat_view_plan import CreateMaterializedViewPlan


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
        optimizer_context = OptimizerContext(self.cost_model, self.rules_manager)
        memo = optimizer_context.memo
        grp_expr = optimizer_context.add_opr_to_group(opr=logical_plan)
        root_grp_id = grp_expr.group_id
        root_expr = memo.groups[root_grp_id].logical_exprs[0]

        # TopDown Rewrite
        # We specify rules that should be applied initially to prevent any interference
        # from other rules. For instance, if we apply the PushDownFilterThroughJoin
        # rule first, it can prevent the XformLateralJoinToLinearFlow rule from being
        # executed because the filter will be pushed to the right child.

        optimizer_context.task_stack.push(
            TopDownRewrite(
                root_expr, self.rules_manager.stage_one_rewrite_rules, optimizer_context
            )
        )
        self.execute_task_stack(optimizer_context.task_stack)

        # BottomUp Rewrite
        root_expr = memo.groups[root_grp_id].logical_exprs[0]
        optimizer_context.task_stack.push(
            BottomUpRewrite(
                root_expr, self.rules_manager.stage_two_rewrite_rules, optimizer_context
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

    # Disable exchange plan if there is a branch.
    def post_process(self, physical_plan: AbstractPlan):
        # Detect whether there is a branch.
        is_branch, is_create_mat = False, False
        for plan_node in physical_plan.walk():
            if len(plan_node.children) > 1:
                is_branch = True
                break
            if isinstance(plan_node, CreateMaterializedViewPlan):
                is_create_mat = True

        # Replace exchange plan.
        if is_branch or is_create_mat:

            def _recursive_strip_exchange(plan: AbstractPlan, is_top: bool = False):
                children = []
                for child_plan in plan.children:
                    return_child_list = _recursive_strip_exchange(child_plan)
                    children += return_child_list

                plan.clear_children()
                for child in children:
                    plan.append_child(child)

                if isinstance(plan, ExchangePlan):
                    assert (
                        not is_top or len(plan.children) == 1
                    ), "Top ExchangePlan can only have 1 child."
                    return plan.children
                else:
                    return [plan]

            return _recursive_strip_exchange(physical_plan, True)[0]
        else:
            return physical_plan

    def build(self, logical_plan: Operator):
        # apply optimizations
        plan = self.optimize(logical_plan)

        # Only run post-processing if Ray is enabled.
        if ConfigurationManager().get_value("experimental", "ray"):
            plan = self.post_process(plan)

        return plan
