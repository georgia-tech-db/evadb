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
import unittest
from test.util import create_sample_video, load_inbuilt_udfs

from mock import MagicMock

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.experimental.ray.optimizer.rules.rules import LogicalExchangeToPhysical
from eva.optimizer.operators import (
    LogicalFilter,
    LogicalGet,
    LogicalProject,
    LogicalQueryDerivedGet,
)
from eva.optimizer.rules.rules import (
    EmbedFilterIntoDerivedGet,
    EmbedFilterIntoGet,
    EmbedProjectIntoDerivedGet,
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
    LogicalGetToSeqScan,
    LogicalGroupByToPhysical,
    LogicalInnerJoinCommutativity,
    LogicalInsertToPhysical,
    LogicalJoinToPhysicalHashJoin,
    LogicalLateralJoinToPhysical,
    LogicalLimitToPhysical,
    LogicalLoadToPhysical,
    LogicalOrderByToPhysical,
    LogicalProjectToPhysical,
    LogicalRenameToPhysical,
    LogicalSampleToUniformSample,
    LogicalShowToPhysical,
    LogicalUnionToPhysical,
    LogicalUploadToPhysical,
    Promise,
    PushDownFilterThroughApplyAndMerge,
    PushDownFilterThroughJoin,
    XformLateralJoinToLinearFlow,
)
from eva.optimizer.rules.rules_manager import RulesManager
from eva.server.command_handler import execute_query_fetch_all


class TestRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        video_file_path = create_sample_video()
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(load_query)
        load_inbuilt_udfs()

    @classmethod
    def tearDownClass(cls):
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    def test_rules_promises_order(self):
        # Promise of all rewrite should be greater than implementation
        self.assertTrue(
            Promise.EMBED_FILTER_INTO_DERIVED_GET > Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.EMBED_PROJECT_INTO_DERIVED_GET > Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.EMBED_SAMPLE_INTO_GET > Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.EMBED_FILTER_INTO_GET > Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.EMBED_PROJECT_INTO_GET > Promise.IMPLEMENTATION_DELIMETER
        )

        # Promise of implementation rules should be lesser than rewrite rules
        self.assertTrue(
            Promise.LOGICAL_CREATE_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_CREATE_UDF_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_DERIVED_GET_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_GET_TO_SEQSCAN < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_INSERT_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_LIMIT_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_GROUPBY_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_ORDERBY_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_SAMPLE_TO_UNIFORMSAMPLE < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_LOAD_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_UPLOAD_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_UNION_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_RENAME_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_DROP_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_EXPLAIN_TO_PHYSICAL < Promise.IMPLEMENTATION_DELIMETER
        )
        self.assertTrue(
            Promise.LOGICAL_CREATE_INDEX_TO_FAISS < Promise.IMPLEMENTATION_DELIMETER
        )

    def test_supported_rules(self):
        # adding/removing rules should update this test
        supported_rewrite_rules = [
            EmbedFilterIntoGet(),
            #    EmbedFilterIntoDerivedGet(),
            EmbedProjectIntoGet(),
            EmbedSampleIntoGet(),
            #    EmbedProjectIntoDerivedGet(),
            XformLateralJoinToLinearFlow(),
            PushDownFilterThroughApplyAndMerge(),
            PushDownFilterThroughJoin(),
        ]
        self.assertEqual(
            len(supported_rewrite_rules), len(RulesManager().rewrite_rules)
        )
        # check all the rule instance exists
        for rule in supported_rewrite_rules:
            self.assertTrue(
                any(isinstance(rule, type(x)) for x in RulesManager().rewrite_rules)
            )

        supported_logical_rules = [LogicalInnerJoinCommutativity()]
        self.assertEqual(
            len(supported_logical_rules), len(RulesManager().logical_rules)
        )

        for rule in supported_logical_rules:
            self.assertTrue(
                any(isinstance(rule, type(x)) for x in RulesManager().logical_rules)
            )

        supported_implementation_rules = [
            LogicalCreateToPhysical(),
            LogicalRenameToPhysical(),
            LogicalDropToPhysical(),
            LogicalCreateUDFToPhysical(),
            LogicalDropUDFToPhysical(),
            LogicalInsertToPhysical(),
            LogicalLoadToPhysical(),
            LogicalUploadToPhysical(),
            LogicalSampleToUniformSample(),
            LogicalGetToSeqScan(),
            LogicalDerivedGetToPhysical(),
            LogicalUnionToPhysical(),
            LogicalGroupByToPhysical(),
            LogicalOrderByToPhysical(),
            LogicalLimitToPhysical(),
            LogicalLateralJoinToPhysical(),
            LogicalFunctionScanToPhysical(),
            LogicalJoinToPhysicalHashJoin(),
            LogicalCreateMaterializedViewToPhysical(),
            LogicalFilterToPhysical(),
            LogicalProjectToPhysical(),
            LogicalShowToPhysical(),
            LogicalExplainToPhysical(),
            LogicalCreateIndexToFaiss(),
            LogicalApplyAndMergeToPhysical()
        ]

        ray_enabled = ConfigurationManager().get_value("experimental", "ray")
        if ray_enabled:
            supported_implementation_rules.append(LogicalExchangeToPhysical())
        self.assertEqual(
            len(supported_implementation_rules),
            len(RulesManager().implementation_rules),
        )

        for rule in supported_implementation_rules:
            self.assertTrue(
                any(
                    isinstance(rule, type(x))
                    for x in RulesManager().implementation_rules
                )
            )

    # EmbedProjectIntoGet
    def test_simple_project_into_get(self):
        rule = EmbedProjectIntoGet()
        expr1 = MagicMock()
        expr2 = MagicMock()
        expr3 = MagicMock()

        logi_get = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        logi_project = LogicalProject([expr1, expr2, expr3], [logi_get])

        rewrite_opr = rule.apply(logi_project, MagicMock())
        self.assertFalse(rewrite_opr is logi_get)
        self.assertEqual(rewrite_opr.target_list, [expr1, expr2, expr3])

    # EmbedFilterIntoGet
    def test_simple_filter_into_get(self):
        rule = EmbedFilterIntoGet()
        predicate = MagicMock()

        logi_get = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        logi_filter = LogicalFilter(predicate, [logi_get])

        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertFalse(rewrite_opr is logi_get)
        self.assertEqual(rewrite_opr.predicate, predicate)

    # EmbedFilterIntoDerivedGet
    def test_simple_filter_into_derived_get(self):
        rule = EmbedFilterIntoDerivedGet()
        predicate = MagicMock()

        logi_derived_get = LogicalQueryDerivedGet(MagicMock())
        logi_filter = LogicalFilter(predicate, [logi_derived_get])

        rewrite_opr = rule.apply(logi_filter, MagicMock())
        self.assertFalse(rewrite_opr is logi_derived_get)
        self.assertEqual(rewrite_opr.predicate, predicate)

    # EmbedProjectIntoDerivedGet
    def test_simple_project_into_derived_get(self):
        rule = EmbedProjectIntoDerivedGet()
        target_list = MagicMock()

        logi_derived_get = LogicalQueryDerivedGet(MagicMock())
        logi_project = LogicalProject(target_list, [logi_derived_get])

        rewrite_opr = rule.apply(logi_project, MagicMock())
        self.assertFalse(rewrite_opr is logi_derived_get)
        self.assertEqual(rewrite_opr.target_list, target_list)
