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
from eva.experimental.ray.optimizer.rules.rules import LogicalExchangeToPhysical
from eva.experimental.ray.optimizer.rules.rules import (
    LogicalGetToSeqScan as DistributedLogicalGetToSeqScan,
)
from eva.experimental.ray.optimizer.rules.rules import (
    LogicalProjectToPhysical as DistributedLogicalProjectToPhysical,
)
from eva.optimizer.rules.rules import (
    CombineSimilarityOrderByAndLimitToFaissIndexScan,
    EmbedFilterIntoGet,
    EmbedProjectIntoGet,
    EmbedSampleIntoGet,
    LogicalApplyAndMergeToPhysical,
    LogicalCreateIndexToFaiss,
    LogicalCreateMaterializedViewToPhysical,
    LogicalCreateToPhysical,
    LogicalCreateUDFToPhysical,
    LogicalDerivedGetToPhysical,
    LogicalDropToPhysical,
    LogicalDropUDFToPhysical,
    LogicalExplainToPhysical,
    LogicalFaissIndexScanToPhysical,
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
    LogicalLateralJoinToPhysical,
    LogicalLimitToPhysical,
    LogicalLoadToPhysical,
    LogicalOrderByToPhysical,
)
from eva.optimizer.rules.rules import (
    LogicalProjectToPhysical as SequentialLogicalProjectToPhysical,
)
from eva.optimizer.rules.rules import (
    LogicalRenameToPhysical,
    LogicalSampleToUniformSample,
    LogicalShowToPhysical,
    LogicalUnionToPhysical,
    LogicalUploadToPhysical,
    PushDownFilterThroughApplyAndMerge,
    PushDownFilterThroughJoin,
    XformLateralJoinToLinearFlow,
)
from eva.optimizer.rules.rules_base import Rule


class RulesManager:
    def __init__(self):
        self._logical_rules = [LogicalInnerJoinCommutativity()]

        self._rewrite_rules = [
            EmbedFilterIntoGet(),
            # EmbedFilterIntoDerivedGet(),
            EmbedProjectIntoGet(),
            # EmbedProjectIntoDerivedGet(),
            EmbedSampleIntoGet(),
            PushDownFilterThroughJoin(),
            PushDownFilterThroughApplyAndMerge(),
            XformLateralJoinToLinearFlow(),
            CombineSimilarityOrderByAndLimitToFaissIndexScan(),
        ]

        ray_enabled = ConfigurationManager().get_value("experimental", "ray")

        self._implementation_rules = [
            LogicalCreateToPhysical(),
            LogicalRenameToPhysical(),
            LogicalDropToPhysical(),
            LogicalCreateUDFToPhysical(),
            LogicalDropUDFToPhysical(),
            LogicalInsertToPhysical(),
            LogicalLoadToPhysical(),
            LogicalUploadToPhysical(),
            LogicalSampleToUniformSample(),
            DistributedLogicalGetToSeqScan()
            if ray_enabled
            else SequentialLogicalGetToSeqScan(),
            LogicalDerivedGetToPhysical(),
            LogicalUnionToPhysical(),
            LogicalGroupByToPhysical(),
            LogicalOrderByToPhysical(),
            LogicalLimitToPhysical(),
            LogicalLateralJoinToPhysical(),
            LogicalJoinToPhysicalHashJoin(),
            LogicalFunctionScanToPhysical(),
            LogicalCreateMaterializedViewToPhysical(),
            LogicalFilterToPhysical(),
            DistributedLogicalProjectToPhysical()
            if ray_enabled
            else SequentialLogicalProjectToPhysical(),
            LogicalShowToPhysical(),
            LogicalExplainToPhysical(),
            LogicalCreateIndexToFaiss(),
            LogicalApplyAndMergeToPhysical(),
            LogicalFaissIndexScanToPhysical(),
        ]

        if ray_enabled:
            self._implementation_rules.append(LogicalExchangeToPhysical())
        self._all_rules = (
            self._rewrite_rules + self._logical_rules + self._implementation_rules
        )

    @property
    def rewrite_rules(self):
        return self._rewrite_rules

    @property
    def implementation_rules(self):
        return self._implementation_rules

    @property
    def logical_rules(self):
        return self._logical_rules

    @property
    def all_rules(self):
        return self._all_rules

    def disable_rules(self, rules: List[Rule]):
        def _remove_from_list(rule_list, rule_to_remove):
            for rule in rule_list:
                if rule.rule_type == rule_to_remove.rule_type:
                    rule_list.remove(rule)

        for rule in rules:
            if rule.is_implementation_rule():
                _remove_from_list(self.implementation_rules, rule)
            elif rule.is_rewrite_rule():
                _remove_from_list(self.rewrite_rules, rule)
            elif rule.is_logical_rule(rule):
                _remove_from_list(self.logical_rules, rule)
            else:
                raise Exception(f"Provided Invalid rule {rule}")

    def add_rules(self, rules: List[Rule]):
        def _add_to_list(rule_list, rule_to_remove):
            if any([rule.rule_type != rule_to_remove.rule_type for rule in rule_list]):
                rule_list.append(rule)

        for rule in rules:
            if rule.is_implementation_rule():
                _add_to_list(self.implementation_rules, rule)
            elif rule.is_rewrite_rule():
                _add_to_list(self.rewrite_rules, rule)
            elif rule.is_logical_rule(rule):
                _add_to_list(self.logical_rules, rule)
            else:
                raise Exception(f"Provided Invalid rule {rule}")


@contextmanager
def disable_rules(rules: List[Rule]):
    """Use this function to temporarily drop rules.
        Useful for testing and debugging purposes.
    Args:
        rules (List[Rule]): List of rules to temporirly drop
    """
    try:
        rules_manager = RulesManager()
        rules_manager.disable_rules(rules)
        yield rules_manager
    finally:
        rules_manager.add_rules(rules)
