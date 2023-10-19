# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from dataclasses import dataclass
from functools import singledispatch

from evadb.optimizer.group_expression import GroupExpression
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.apply_and_merge_plan import ApplyAndMergePlan
from evadb.plan_nodes.hash_join_build_plan import HashJoinBuildPlan
from evadb.plan_nodes.hash_join_probe_plan import HashJoinProbePlan
from evadb.plan_nodes.nested_loop_join_plan import NestedLoopJoinPlan
from evadb.plan_nodes.seq_scan_plan import SeqScanPlan
from evadb.plan_nodes.storage_plan import StoragePlan


@dataclass
class CostEntry:
    plan_cost: float = 1.0
    amortize_factor: float = 1.0


class CostModel:
    """
    Basic cost model. Change it as we add more cost based rules
    """

    def __init__(self):
        pass

    def calculate_cost(self, gexpr: GroupExpression) -> CostEntry:
        """
        Return the cost of the group expression.
        """

        @singledispatch
        def cost(opr: AbstractPlan):
            return CostEntry(plan_cost=1.0)

        @cost.register(NestedLoopJoinPlan)
        def cost_nested_loop_join_build_plan(opr: NestedLoopJoinPlan):
            return CostEntry(plan_cost=1.0)

        @cost.register(HashJoinBuildPlan)
        def cost_hash_join_build_plan(opr: HashJoinBuildPlan):
            return CostEntry(plan_cost=1.0)

        @cost.register(HashJoinProbePlan)
        def cost_hash_join_probe_plan(opr: HashJoinProbePlan):
            return CostEntry(plan_cost=1.0)

        @cost.register(SeqScanPlan)
        def cost_seq_scan(opr: SeqScanPlan):
            return CostEntry(plan_cost=1.0)

        @cost.register(StoragePlan)
        def cost_storage_plan(opr: StoragePlan):
            return CostEntry(
                plan_cost=opr.batch_mem_size, amortize_factor=1.0 / opr.batch_mem_size
            )

        @cost.register(ApplyAndMergePlan)
        def cost_apply_and_merge(opr: ApplyAndMergePlan):
            if opr.func_expr.has_cache():
                return CostEntry(plan_cost=0)
            return CostEntry(plan_cost=1.0)

        return cost(gexpr.opr)
