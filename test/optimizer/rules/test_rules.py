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
from test.util import create_sample_video, load_udfs_for_testing

import pytest
from mock import MagicMock, patch

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.configuration.configuration_manager import ConfigurationManager
from eva.experimental.ray.optimizer.rules.rules import LogicalExchangeToPhysical
from eva.experimental.ray.optimizer.rules.rules import (
    LogicalGetToSeqScan as DistributedLogicalGetToSeqScan,
)
from eva.experimental.ray.optimizer.rules.rules import (
    LogicalProjectToPhysical as DistributedLogicalProjectToPhysical,
)
from eva.optimizer.operators import (
    LogicalFilter,
    LogicalGet,
    LogicalJoin,
    LogicalSample,
)
from eva.optimizer.rules.rules import (
    CacheFunctionExpressionInApply,
    CombineSimilarityOrderByAndLimitToFaissIndexScan,
    EmbedFilterIntoGet,
    EmbedSampleIntoGet,
    LogicalApplyAndMergeToPhysical,
    LogicalCreateIndexToFaiss,
    LogicalCreateMaterializedViewToPhysical,
    LogicalCreateToPhysical,
    LogicalCreateUDFToPhysical,
    LogicalDeleteToPhysical,
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
    LogicalJoinToPhysicalNestedLoopJoin,
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
    LogicalShowToPhysical,
    LogicalUnionToPhysical,
    Promise,
    PushDownFilterThroughApplyAndMerge,
    PushDownFilterThroughJoin,
    ReorderPredicates,
    Rule,
    RuleType,
    XformLateralJoinToLinearFlow,
)
from eva.optimizer.rules.rules_manager import RulesManager, disable_rules
from eva.parser.types import JoinType
from eva.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class RulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # reset the catalog manager before running each test
        CatalogManager().reset()
        video_file_path = create_sample_video()
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(load_query)
        load_udfs_for_testing(mode="minimal")

    @classmethod
    def tearDownClass(cls):
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    def test_rules_promises_order(self):
        # Promise of all rewrite should be greater than implementation
        rewrite_promises = [
            Promise.LOGICAL_INNER_JOIN_COMMUTATIVITY,
            Promise.EMBED_FILTER_INTO_GET,
            Promise.EMBED_SAMPLE_INTO_GET,
            Promise.XFORM_LATERAL_JOIN_TO_LINEAR_FLOW,
            Promise.PUSHDOWN_FILTER_THROUGH_JOIN,
            Promise.PUSHDOWN_FILTER_THROUGH_APPLY_AND_MERGE,
            Promise.COMBINE_SIMILARITY_ORDERBY_AND_LIMIT_TO_FAISS_INDEX_SCAN,
            Promise.REORDER_PREDICATES,
        ]

        for promise in rewrite_promises:
            self.assertTrue(promise > Promise.IMPLEMENTATION_DELIMETER)

        # Promise of implementation rules should be lesser than rewrite rules
        implementation_promises = [
            Promise.LOGICAL_EXCHANGE_TO_PHYSICAL,
            Promise.LOGICAL_UNION_TO_PHYSICAL,
            Promise.LOGICAL_MATERIALIZED_VIEW_TO_PHYSICAL,
            Promise.LOGICAL_GROUPBY_TO_PHYSICAL,
            Promise.LOGICAL_ORDERBY_TO_PHYSICAL,
            Promise.LOGICAL_LIMIT_TO_PHYSICAL,
            Promise.LOGICAL_INSERT_TO_PHYSICAL,
            Promise.LOGICAL_DELETE_TO_PHYSICAL,
            Promise.LOGICAL_RENAME_TO_PHYSICAL,
            Promise.LOGICAL_DROP_TO_PHYSICAL,
            Promise.LOGICAL_LOAD_TO_PHYSICAL,
            Promise.LOGICAL_CREATE_TO_PHYSICAL,
            Promise.LOGICAL_CREATE_UDF_TO_PHYSICAL,
            Promise.LOGICAL_SAMPLE_TO_UNIFORMSAMPLE,
            Promise.LOGICAL_GET_TO_SEQSCAN,
            Promise.LOGICAL_DERIVED_GET_TO_PHYSICAL,
            Promise.LOGICAL_LATERAL_JOIN_TO_PHYSICAL,
            Promise.LOGICAL_JOIN_TO_PHYSICAL_HASH_JOIN,
            Promise.LOGICAL_JOIN_TO_PHYSICAL_NESTED_LOOP_JOIN,
            Promise.LOGICAL_FUNCTION_SCAN_TO_PHYSICAL,
            Promise.LOGICAL_FILTER_TO_PHYSICAL,
            Promise.LOGICAL_PROJECT_TO_PHYSICAL,
            Promise.LOGICAL_SHOW_TO_PHYSICAL,
            Promise.LOGICAL_DROP_UDF_TO_PHYSICAL,
            Promise.LOGICAL_EXPLAIN_TO_PHYSICAL,
            Promise.LOGICAL_CREATE_INDEX_TO_FAISS,
            Promise.LOGICAL_APPLY_AND_MERGE_TO_PHYSICAL,
            Promise.LOGICAL_FAISS_INDEX_SCAN_TO_PHYSICAL,
        ]

        for promise in implementation_promises:
            self.assertTrue(promise < Promise.IMPLEMENTATION_DELIMETER)

        promise_count = len(Promise)
        rewrite_count = len(set(rewrite_promises))
        implementation_count = len(set(implementation_promises))

        # rewrite_count + implementation_count + 1 (for IMPLEMENTATION_DELIMETER)
        self.assertEqual(rewrite_count + implementation_count + 2, promise_count)

    def test_supported_rules(self):
        # adding/removing rules should update this test
        supported_rewrite_rules = [
            EmbedFilterIntoGet(),
            #    EmbedFilterIntoDerivedGet(),
            EmbedSampleIntoGet(),
            XformLateralJoinToLinearFlow(),
            PushDownFilterThroughApplyAndMerge(),
            PushDownFilterThroughJoin(),
            CombineSimilarityOrderByAndLimitToFaissIndexScan(),
            ReorderPredicates(),
        ]
        rewrite_rules = (
            RulesManager().stage_one_rewrite_rules
            + RulesManager().stage_two_rewrite_rules
        )
        self.assertEqual(
            len(supported_rewrite_rules),
            len(rewrite_rules),
        )
        # check all the rule instance exists
        for rule in supported_rewrite_rules:
            self.assertTrue(any(isinstance(rule, type(x)) for x in rewrite_rules))

        supported_logical_rules = [
            LogicalInnerJoinCommutativity(),
            CacheFunctionExpressionInApply(),
        ]
        self.assertEqual(
            len(supported_logical_rules), len(RulesManager().logical_rules)
        )

        for rule in supported_logical_rules:
            self.assertTrue(
                any(isinstance(rule, type(x)) for x in RulesManager().logical_rules)
            )

        ray_enabled = ConfigurationManager().get_value("experimental", "ray")

        # For the current version, we choose either the distributed or the
        # sequential rule, because we do not have a logic to choose one over
        # the other in the current optimizer. Sequential rewrite is currently
        # embedded inside distributed rule if ray is enabled. The rule itself
        # has some simple heuristics to choose one over the other.
        supported_implementation_rules = [
            LogicalCreateToPhysical(),
            LogicalRenameToPhysical(),
            LogicalDropToPhysical(),
            LogicalCreateUDFToPhysical(),
            LogicalDropUDFToPhysical(),
            LogicalInsertToPhysical(),
            LogicalDeleteToPhysical(),
            LogicalLoadToPhysical(),
            DistributedLogicalGetToSeqScan()
            if ray_enabled
            else SequentialLogicalGetToSeqScan(),
            LogicalDerivedGetToPhysical(),
            LogicalUnionToPhysical(),
            LogicalGroupByToPhysical(),
            LogicalOrderByToPhysical(),
            LogicalLimitToPhysical(),
            LogicalJoinToPhysicalNestedLoopJoin(),
            LogicalLateralJoinToPhysical(),
            LogicalFunctionScanToPhysical(),
            LogicalJoinToPhysicalHashJoin(),
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

    # EmbedFilterIntoGet
    def test_simple_filter_into_get(self):
        rule = EmbedFilterIntoGet()
        predicate = MagicMock()

        logi_get = LogicalGet(MagicMock(), MagicMock(), MagicMock())
        logi_filter = LogicalFilter(predicate, [logi_get])

        rewrite_opr = next(rule.apply(logi_filter, MagicMock()))
        self.assertFalse(rewrite_opr is logi_get)
        self.assertEqual(rewrite_opr.predicate, predicate)

    def test_embed_sample_into_get_does_not_work_with_structured_data(self):
        rule = EmbedSampleIntoGet()

        table_obj = TableCatalogEntry(
            name="foo", table_type=TableType.STRUCTURED_DATA, file_url=MagicMock()
        )

        logi_get = LogicalGet(MagicMock(), table_obj, MagicMock(), MagicMock())
        logi_sample = LogicalSample(MagicMock(), MagicMock(), children=[logi_get])

        self.assertFalse(rule.check(logi_sample, MagicMock()))

    def test_disable_rules(self):
        with disable_rules([PushDownFilterThroughApplyAndMerge()]) as rules_manager:
            self.assertFalse(
                any(
                    isinstance(PushDownFilterThroughApplyAndMerge, type(x))
                    for x in rules_manager.stage_two_rewrite_rules
                )
            )

    def test_xform_lateral_join_does_not_work_with_other_join(self):
        rule = XformLateralJoinToLinearFlow()
        logi_join = LogicalJoin(JoinType.INNER_JOIN)
        self.assertFalse(rule.check(logi_join, MagicMock()))

    def test_rule_base_errors(self):
        with patch.object(Rule, "__abstractmethods__", set()):
            rule = Rule(rule_type=RuleType.INVALID_RULE)
            with self.assertRaises(NotImplementedError):
                rule.promise()
            with self.assertRaises(NotImplementedError):
                rule.check(MagicMock(), MagicMock())
            with self.assertRaises(NotImplementedError):
                rule.apply(MagicMock())
