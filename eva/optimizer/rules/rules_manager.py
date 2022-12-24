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

    logical_rules = [LogicalInnerJoinCommutativity()]

    rewrite_rules = [
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

    implementation_rules = [
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
        implementation_rules.append(LogicalExchangeToPhysical())

    all_rules = rewrite_rules + logical_rules + implementation_rules

    @classmethod
    def disable_rules(cls, rules: List[Rule]):
        def _remove_from_list(rule_list, rule_to_remove):
            for rule in rule_list:
                if rule.rule_type == rule_to_remove.rule_type:
                    rule_list.remove(rule)

        for rule in rules:
            if rule.is_implementation_rule():
                _remove_from_list(cls.implementation_rules, rule)
            elif rule.is_rewrite_rule():
                _remove_from_list(cls.rewrite_rules, rule)
            elif rule.is_logical_rule(rule):
                _remove_from_list(cls.logical_rules, rule)
            else:
                raise Exception(f"Provided Invalid rule {rule}")

    @classmethod
    def add_rules(cls, rules: List[Rule]):
        def _add_to_list(rule_list, rule_to_remove):
            if any([rule.rule_type != rule_to_remove.rule_type for rule in rule_list]):
                rule_list.append(rule)

        for rule in rules:
            if rule.is_implementation_rule():
                _add_to_list(cls.implementation_rules, rule)
            elif rule.is_rewrite_rule():
                _add_to_list(cls.rewrite_rules, rule)
            elif rule.is_logical_rule(rule):
                _add_to_list(cls.logical_rules, rule)
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
        RulesManager.disable_rules(rules)
        yield
    finally:
        RulesManager.add_rules(rules)
