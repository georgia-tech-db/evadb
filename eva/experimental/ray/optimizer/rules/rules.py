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
from __future__ import annotations

from typing import TYPE_CHECKING

from eva.optimizer.rules.pattern import Pattern

if TYPE_CHECKING:
    from eva.optimizer.optimizer_context import OptimizerContext

from eva.executor.execution_context import Context
from eva.experimental.ray.planner.exchange_plan import ExchangePlan
from eva.expression.function_expression import FunctionExpression
from eva.optimizer.operators import (
    LogicalExchange,
    LogicalGet,
    LogicalProject,
    OperatorType,
)
from eva.optimizer.rules.rules_base import Promise, Rule, RuleType
from eva.plan_nodes.project_plan import ProjectPlan
from eva.plan_nodes.seq_scan_plan import SeqScanPlan
from eva.plan_nodes.storage_plan import StoragePlan


class LogicalExchangeToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALEXCHANGE)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_EXCHANGE_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_EXCHANGE_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalExchange, context: OptimizerContext):
        after = ExchangePlan(before.view)
        for child in before.children:
            after.append_child(child)
        yield after


class LogicalProjectToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALPROJECT)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_PROJECT_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_PROJECT_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalProject, context: OptimizerContext):
        after = ProjectPlan(before.target_list)
        for child in before.children:
            after.append_child(child)
        upper = ExchangePlan(
            parallelism=1,
            ray_conf={"num_gpus": 1} if Context().gpus else {"num_cpus": 1},
        )
        upper.append_child(after)
        yield upper


class LogicalGetToSeqScan(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICALGET)
        super().__init__(RuleType.LOGICAL_GET_TO_SEQSCAN, pattern)

    def promise(self):
        return Promise.LOGICAL_GET_TO_SEQSCAN

    def check(self, before: LogicalGet, context: OptimizerContext):
        return True

    def apply(self, before: LogicalGet, context: OptimizerContext):
        # Configure the batch_mem_size. It decides the number of rows
        # read in a batch from storage engine.
        # ToDO: Experiment heuristics.
        scan = SeqScanPlan(None, before.target_list, before.alias)
        lower = ExchangePlan(parallelism=1)
        lower.append_child(
            StoragePlan(
                before.table_obj,
                before.video,
                predicate=before.predicate,
                sampling_rate=before.sampling_rate,
            )
        )
        scan.append_child(lower)
        # Check whether the projection contains a UDF
        if before.target_list is None or not any(
            [isinstance(expr, FunctionExpression) for expr in before.target_list]
        ):
            yield scan
        else:
            upper = ExchangePlan(
                parallelism=2,
                ray_conf={"num_gpus": 1}
                if len(Context().gpus) >= 2
                else {"num_cpus": 1},
            )
            upper.append_child(scan)
            yield upper
