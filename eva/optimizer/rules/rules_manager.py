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

from contextlib import contextmanager
from typing import List

from eva.configuration.configuration_manager import ConfigurationManager
from eva.experimental.parallel.optimizer.rules.rules import (
    LogicalApplyAndMergeToPhysical as ParallelLogicalApplyAndMergeToPhysical,
)
from eva.experimental.parallel.optimizer.rules.rules import LogicalExchangeToPhysical
from eva.experimental.parallel.optimizer.rules.rules import (
    LogicalGetToSeqScan as ParallelLogicalGetToSeqScan,
)
from eva.optimizer.rules.rules import (
    CacheFunctionExpressionInApply,
    CacheFunctionExpressionInFilter,
    CacheFunctionExpressionInProject,
    CombineSimilarityOrderByAndLimitToVectorIndexScan,
    EmbedFilterIntoGet,
    EmbedSampleIntoGet,
)
from eva.optimizer.rules.rules import (
    LogicalApplyAndMergeToPhysical as SequentialLogicalApplyAndMergeToPhysical,
)
from eva.optimizer.rules.rules import (
    LogicalCreateIndexToVectorIndex,
    LogicalCreateMaterializedViewToPhysical,
    LogicalCreateToPhysical,
    LogicalCreateUDFToPhysical,
    LogicalDeleteToPhysical,
    LogicalDerivedGetToPhysical,
    LogicalDropToPhysical,
    LogicalDropUDFToPhysical,
    LogicalExplainToPhysical,
    LogicalFilterToPhysical,
    LogicalFunctionScanToPhysical,
)
from eva.optimizer.rules.rules import (
    LogicalGetToSeqScan as SequentialLogicalGetToSeqScan,
)
from eva.optimizer.rules.rules import (
    LogicalGroupByToPhysical,
    LogicalInnerJoinCommutativity,
    LogicalInsertToPhysical,
    LogicalJoinToPhysicalHashJoin,
    LogicalJoinToPhysicalNestedLoopJoin,
    LogicalLateralJoinToPhysical,
    LogicalLimitToPhysical,
    LogicalLoadToPhysical,
    LogicalOrderByToPhysical,
    LogicalProjectToPhysical,
    LogicalRenameToPhysical,
    LogicalShowToPhysical,
    LogicalUnionToPhysical,
    LogicalVectorIndexScanToPhysical,
    PushDownFilterThroughApplyAndMerge,
    PushDownFilterThroughJoin,
    ReorderPredicates,
    XformExtractObjectToLinearFlow,
    XformLateralJoinToLinearFlow,
)
from eva.optimizer.rules.rules_base import Rule


class RulesManager:
    def __init__(self):
        self._logical_rules = [
            LogicalInnerJoinCommutativity(),
            CacheFunctionExpressionInApply(),
            CacheFunctionExpressionInFilter(),
            CacheFunctionExpressionInProject(),
        ]

        self._stage_one_rewrite_rules = [
            XformLateralJoinToLinearFlow(),
            XformExtractObjectToLinearFlow(),
        ]

        self._stage_two_rewrite_rules = [
            EmbedFilterIntoGet(),
            # EmbedFilterIntoDerivedGet(),
            EmbedSampleIntoGet(),
            PushDownFilterThroughJoin(),
            PushDownFilterThroughApplyAndMerge(),
            CombineSimilarityOrderByAndLimitToVectorIndexScan(),
            ReorderPredicates(),
        ]

        ray_enabled = ConfigurationManager().get_value("experimental", "ray")

        self._implementation_rules = [
            LogicalCreateToPhysical(),
            LogicalRenameToPhysical(),
            LogicalDropToPhysical(),
            LogicalCreateUDFToPhysical(),
            LogicalDropUDFToPhysical(),
            LogicalInsertToPhysical(),
            LogicalDeleteToPhysical(),
            LogicalLoadToPhysical(),
            ParallelLogicalGetToSeqScan()
            if ray_enabled
            else SequentialLogicalGetToSeqScan(),
            LogicalDerivedGetToPhysical(),
            LogicalUnionToPhysical(),
            LogicalGroupByToPhysical(),
            LogicalOrderByToPhysical(),
            LogicalLimitToPhysical(),
            LogicalJoinToPhysicalNestedLoopJoin(),
            LogicalLateralJoinToPhysical(),
            LogicalJoinToPhysicalHashJoin(),
            LogicalFunctionScanToPhysical(),
            LogicalCreateMaterializedViewToPhysical(),
            LogicalFilterToPhysical(),
            LogicalProjectToPhysical(),
            ParallelLogicalApplyAndMergeToPhysical()
            if ray_enabled
            else SequentialLogicalApplyAndMergeToPhysical(),
            LogicalShowToPhysical(),
            LogicalExplainToPhysical(),
            LogicalCreateIndexToVectorIndex(),
            LogicalVectorIndexScanToPhysical(),
        ]

        if ray_enabled:
            self._implementation_rules.append(LogicalExchangeToPhysical())
        self._all_rules = (
            self._stage_one_rewrite_rules
            + self._stage_two_rewrite_rules
            + self._logical_rules
            + self._implementation_rules
        )

    @property
    def stage_one_rewrite_rules(self):
        return self._stage_one_rewrite_rules

    @property
    def stage_two_rewrite_rules(self):
        return self._stage_two_rewrite_rules

    @property
    def implementation_rules(self):
        return self._implementation_rules

    @property
    def logical_rules(self):
        return self._logical_rules

    def disable_rules(self, rules: List[Rule]):
        def _remove_from_list(rule_list, rule_to_remove):
            for rule in rule_list:
                if rule.rule_type == rule_to_remove.rule_type:
                    rule_list.remove(rule)

        for rule in rules:
            assert (
                rule.is_implementation_rule()
                or rule.is_stage_one_rewrite_rules()
                or rule.is_stage_two_rewrite_rules()
                or rule.is_logical_rule()
            ), f"Provided Invalid rule {rule}"

            if rule.is_implementation_rule():
                _remove_from_list(self.implementation_rules, rule)
            elif rule.is_stage_one_rewrite_rules():
                _remove_from_list(self.stage_one_rewrite_rules, rule)
            elif rule.is_stage_two_rewrite_rules():
                _remove_from_list(self.stage_two_rewrite_rules, rule)
            elif rule.is_logical_rule():
                _remove_from_list(self.logical_rules, rule)

    def add_rules(self, rules: List[Rule]):
        def _add_to_list(rule_list, rule_to_remove):
            if any([rule.rule_type != rule_to_remove.rule_type for rule in rule_list]):
                rule_list.append(rule)

        for rule in rules:
            assert (
                rule.is_implementation_rule()
                or rule.is_stage_one_rewrite_rules()
                or rule.is_stage_two_rewrite_rules()
                or rule.is_logical_rule()
            ), f"Provided Invalid rule {rule}"

            if rule.is_implementation_rule():
                _add_to_list(self.implementation_rules, rule)
            elif rule.is_stage_one_rewrite_rules():
                _add_to_list(self.stage_one_rewrite_rules, rule)
            elif rule.is_stage_two_rewrite_rules():
                _add_to_list(self.stage_two_rewrite_rules, rule)
            elif rule.is_logical_rule():
                _add_to_list(self.logical_rules, rule)


@contextmanager
def disable_rules(rules: List[Rule]):
    """Use this function to temporarily drop rules.
        Useful for testing and debugging purposes.
    Args:
        rules (List[Rule]): List of rules to temporarily drop
    """
    try:
        rules_manager = RulesManager()
        rules_manager.disable_rules(rules)
        yield rules_manager
    finally:
        rules_manager.add_rules(rules)
