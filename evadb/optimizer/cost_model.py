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
import dataclasses
from functools import singledispatch
from typing import List

from evadb.optimizer.group_expression import GroupExpression
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.apply_and_merge_plan import ApplyAndMergePlan
from evadb.plan_nodes.hash_join_build_plan import HashJoinBuildPlan
from evadb.plan_nodes.hash_join_probe_plan import HashJoinProbePlan
from evadb.plan_nodes.nested_loop_join_plan import NestedLoopJoinPlan
from evadb.plan_nodes.seq_scan_plan import SeqScanPlan
from evadb.plan_nodes.storage_plan import StoragePlan


@dataclasses.dataclass
class CostEntry:
    plan_cost: float = 1.0
    num_calls: float = 1.0

    def __gt__(self, other):
        return self.plan_cost * self.num_calls > other.plan_cost * other.num_calls


class CostModel:
    """
    Basic cost model. Change it as we add more cost based rules
    """

    def __init__(self):
        pass

    @property
    def zero_cost(self) -> CostEntry:
        return CostEntry(plan_cost=0)

    def calculate_cost(
        self, gexpr: GroupExpression, children: List[CostEntry]
    ) -> CostEntry:
        """
        Return the cost of the group expression.
        """

        @singledispatch
        def cost(opr: AbstractPlan, children: List[CostEntry]):
            if len(children) > 1:
                return dataclasses.replace(children[0])
            else:
                return CostEntry()

        @cost.register(NestedLoopJoinPlan)
        def cost_nested_loop_join_build_plan(
            opr: NestedLoopJoinPlan, children: List[CostEntry]
        ):
            new_plan_cost = children[0].plan_cost + 1.0
            return dataclasses.replace(children[0], plan_cost=new_plan_cost)

        @cost.register(HashJoinBuildPlan)
        def cost_hash_join_build_plan(
            opr: HashJoinBuildPlan, children: List[CostEntry]
        ):
            new_plan_cost = children[0].plan_cost + 1.0
            return dataclasses.replace(children[0], plan_cost=new_plan_cost)

        @cost.register(HashJoinProbePlan)
        def cost_hash_join_probe_plan(
            opr: HashJoinProbePlan, children: List[CostEntry]
        ):
            new_plan_cost = children[0].plan_cost + 1.0
            return dataclasses.replace(children[0], plan_cost=new_plan_cost)

        @cost.register(SeqScanPlan)
        def cost_seq_scan(opr: SeqScanPlan, children: List[CostEntry]):
            new_plan_cost = children[0].plan_cost + 1.0
            return dataclasses.replace(children[0], plan_cost=new_plan_cost)

        @cost.register(StoragePlan)
        def cost_storage_plan(opr: StoragePlan, children: List[CostEntry]):
            return CostEntry(
                plan_cost=opr.batch_mem_size, num_calls=1.0 / opr.batch_mem_size
            )

        @cost.register(ApplyAndMergePlan)
        def cost_apply_and_merge(opr: ApplyAndMergePlan, children: List[CostEntry]):
            if opr.func_expr.has_cache():
                return dataclasses.replace(children[0])
            new_plan_cost = children[0].plan_cost + 1.0
            return dataclasses.replace(children[0], plan_cost=new_plan_cost)

        return cost(gexpr.opr, children)
