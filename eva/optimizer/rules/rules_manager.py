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
    """Singelton class to manage all the rules in our system"""

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RulesManager, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

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
        ]

        if ray_enabled:
            self._implementation_rules.append(LogicalExchangeToPhysical())

    @property
    def rewrite_rules(self):
        return self._rewrite_rules.copy()

    @property
    def implementation_rules(self):
        return self._implementation_rules.copy()

    @property
    def logical_rules(self):
        return self._logical_rules.copy()

    @property
    def all_rules(self):
        all_rules = self.rewrite_rules + self.logical_rules + self.implementation_rules
        return all_rules

    def disable_rules(self, rules: List[Rule]):
        def _remove_from_list(rule_list, rule_to_remove):
            for rule in rule_list:
                if rule.rule_type == rule_to_remove.rule_type:
                    rule_list.remove(rule)

        for rule in rules:
            if rule.is_implementation_rule():
                _remove_from_list(self._implementation_rules, rule)
            elif rule.is_rewrite_rule():
                _remove_from_list(self._rewrite_rules, rule)
            elif rule.is_logical_rule(rule):
                _remove_from_list(self._logical_rules, rule)
            else:
                raise Exception(f"Provided Invalid rule {rule}")

    def add_rules(self, rules: List[Rule]):
        def _add_to_list(rule_list, rule_to_remove):
            if any([rule.rule_type != rule_to_remove.rule_type for rule in rule_list]):
                rule_list.append(rule)

        for rule in rules:
            if rule.is_implementation_rule():
                _add_to_list(self._implementation_rules, rule)
            elif rule.is_rewrite_rule():
                _add_to_list(self._rewrite_rules, rule)
            elif rule.is_logical_rule(rule):
                _add_to_list(self._logical_rules, rule)
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
        RulesManager().disable_rules(rules)
        yield
    finally:
        RulesManager().add_rules(rules)
