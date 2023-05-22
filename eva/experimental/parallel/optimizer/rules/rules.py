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
from eva.experimental.parallel.plan_nodes.exchange_plan import ExchangePlan
from eva.expression.function_expression import FunctionExpression
from eva.optimizer.operators import (
    LogicalApplyAndMerge,
    LogicalExchange,
    LogicalGet,
    OperatorType,
)
from eva.optimizer.rules.rules_base import Promise, Rule, RuleType
from eva.plan_nodes.apply_and_merge_plan import ApplyAndMergePlan
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


class LogicalApplyAndMergeToPhysical(Rule):
    def __init__(self):
        pattern = Pattern(OperatorType.LOGICAL_APPLY_AND_MERGE)
        pattern.append_child(Pattern(OperatorType.DUMMY))
        super().__init__(RuleType.LOGICAL_APPLY_AND_MERGE_TO_PHYSICAL, pattern)

    def promise(self):
        return Promise.LOGICAL_APPLY_AND_MERGE_TO_PHYSICAL

    def check(self, grp_id: int, context: OptimizerContext):
        return True

    def apply(self, before: LogicalApplyAndMerge, context: OptimizerContext):
        apply_plan = ApplyAndMergePlan(before.func_expr, before.alias, before.do_unnest)

        parallelism = 2 if len(Context().gpus) > 1 else 1
        ray_parallel_env_conf_dict = [
            {"CUDA_VISIBLE_DEVICES": str(i)} for i in range(parallelism)
        ]

        exchange_plan = ExchangePlan(
            inner_plan=apply_plan,
            parallelism=parallelism,
            ray_pull_env_conf_dict={"CUDA_VISIBLE_DEVICES": "0"},
            ray_parallel_env_conf_dict=ray_parallel_env_conf_dict,
        )
        for child in before.children:
            exchange_plan.append_child(child)

        yield exchange_plan


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
        scan_plan = SeqScanPlan(None, before.target_list, before.alias)
        storage_plan = StoragePlan(
            before.table_obj,
            before.video,
            predicate=before.predicate,
            sampling_rate=before.sampling_rate,
        )
        # Check whether the projection contains a UDF
        if before.target_list is None or not any(
            [isinstance(expr, FunctionExpression) for expr in before.target_list]
        ):
            scan_plan.append_child(storage_plan)
            yield scan_plan
        else:
            parallelism = 2 if len(Context().gpus) > 1 else 1
            ray_parallel_env_conf_dict = [
                {"CUDA_VISIBLE_DEVICES": str(i)} for i in range(parallelism)
            ]

            exchange_plan = ExchangePlan(
                inner_plan=scan_plan,
                parallelism=parallelism,
                ray_pull_env_conf_dict={"CUDA_VISIBLE_DEVICES": "0"},
                ray_parallel_env_conf_dict=ray_parallel_env_conf_dict,
            )
            exchange_plan.append_child(storage_plan)
            yield exchange_plan
