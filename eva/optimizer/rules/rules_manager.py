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
    PushDownFilterThroughJoin,
)


class RulesManager:
    """Singelton class to manage all the rules in our system"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RulesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._logical_rules = [LogicalInnerJoinCommutativity()]

        self._rewrite_rules = [
            EmbedFilterIntoGet(),
            # EmbedFilterIntoDerivedGet(),
            EmbedProjectIntoGet(),
            # EmbedProjectIntoDerivedGet(),
            EmbedSampleIntoGet(),
            PushDownFilterThroughJoin(),
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
