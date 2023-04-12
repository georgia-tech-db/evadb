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
from test.util import get_physical_query_plan, load_udfs_for_testing, shutdown_ray

import pytest
from mock import MagicMock, patch

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.expression.comparison_expression import ComparisonExpression
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.rules.rules import (
    PushDownFilterThroughApplyAndMerge,
    PushDownFilterThroughJoin,
    ReorderPredicates,
    XformLateralJoinToLinearFlow,
)
from eva.optimizer.rules.rules_manager import disable_rules
from eva.plan_nodes.predicate_plan import PredicatePlan
from eva.server.command_handler import execute_query_fetch_all
from eva.utils.stats import Timer


@pytest.mark.notparallel
@pytest.mark.skipif(
    ConfigurationManager().get_value("experimental", "ray"),
    reason="Not necessary for Ray",
)
class OptimizerRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        ua_detrac = f"{EVA_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        execute_query_fetch_all(f"LOAD VIDEO '{ua_detrac}' INTO MyVideo2;")
        load_udfs_for_testing(mode="minimal")

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()
        execute_query_fetch_all("DROP TABLE IF EXISTS MyVideo;")

    @patch("eva.expression.function_expression.FunctionExpression.evaluate")
    def test_should_benefit_from_pushdown(self, evaluate_mock):
        query = """SELECT id, obj.labels
                  FROM MyVideo JOIN LATERAL
                    FastRCNNObjectDetector(data) AS obj(labels, bboxes, scores)
                  WHERE id < 2;"""

        time_with_rule = Timer()
        result_with_rule = None
        with time_with_rule:
            result_with_rule = execute_query_fetch_all(query)

        evaluate_count_with_rule = evaluate_mock.call_count

        time_without_rule = Timer()
        result_without_pushdown_rules = None
        with time_without_rule:
            with disable_rules(
                [PushDownFilterThroughApplyAndMerge(), PushDownFilterThroughJoin()]
            ) as rules_manager:
                custom_plan_generator = PlanGenerator(rules_manager)
                result_without_pushdown_rules = execute_query_fetch_all(
                    query, plan_generator=custom_plan_generator
                )

        self.assertEqual(result_without_pushdown_rules, result_with_rule)

        evaluate_count_without_rule = (
            evaluate_mock.call_count - evaluate_count_with_rule
        )

        # without rule it should be slow as we end up running the function
        # on all the frames
        self.assertGreater(evaluate_count_without_rule, 3 * evaluate_count_with_rule)

        result_without_xform_rule = None
        with disable_rules([XformLateralJoinToLinearFlow()]) as rules_manager:
            custom_plan_generator = PlanGenerator(rules_manager)
            result_without_xform_rule = execute_query_fetch_all(
                query, plan_generator=custom_plan_generator
            )

        self.assertEqual(result_without_xform_rule, result_with_rule)

    def test_should_pushdown_without_pushdown_join_rule(self):
        query = """SELECT id, obj.labels
                    FROM MyVideo JOIN LATERAL
                    FastRCNNObjectDetector(data) AS obj(labels, bboxes, scores)
                    WHERE id < 2;"""

        time_with_rule = Timer()
        result_with_rule = None
        with time_with_rule:
            result_with_rule = execute_query_fetch_all(query)
            query_plan = execute_query_fetch_all(f"EXPLAIN {query}")
        time_without_rule = Timer()
        result_without_pushdown_join_rule = None
        with time_without_rule:
            with disable_rules([PushDownFilterThroughJoin()]) as rules_manager:
                # should use PushDownFilterThroughApplyAndMerge()
                custom_plan_generator = PlanGenerator(rules_manager)
                result_without_pushdown_join_rule = execute_query_fetch_all(
                    query, plan_generator=custom_plan_generator
                )
                query_plan_without_pushdown_join_rule = execute_query_fetch_all(
                    f"EXPLAIN {query}", plan_generator=custom_plan_generator
                )

        self.assertEqual(result_without_pushdown_join_rule, result_with_rule)
        self.assertEqual(query_plan, query_plan_without_pushdown_join_rule)

    @patch("eva.catalog.catalog_manager.CatalogManager.get_udf_cost_catalog_entry")
    def test_should_reorder_predicates(self, mock):
        def _check_reorder(cost_func):
            mock.side_effect = cost_func

            pred_1 = "DummyObjectDetector(data).label = ['person']"
            pred_2 = "DummyMultiObjectDetector(data).labels @> ['person']"

            query = f"SELECT id FROM MyVideo WHERE {pred_2} AND {pred_1};"

            plan = get_physical_query_plan(query)
            predicate_plans = list(plan.find_all(PredicatePlan))
            self.assertEqual(len(predicate_plans), 1)

            left: ComparisonExpression = predicate_plans[0].predicate.children[0]
            right: ComparisonExpression = predicate_plans[0].predicate.children[1]

            # predicates reordered based on the cost
            self.assertEqual(left.children[0].name, "DummyObjectDetector")
            self.assertEqual(right.children[0].name, "DummyMultiObjectDetector")

        # reordering if first predicate has higher cost
        _check_reorder(
            lambda name: MagicMock(cost=10)
            if name == "DummyMultiObjectDetector"
            else MagicMock(cost=5)
        )

        # reordering if first predicate has no cost
        _check_reorder(
            lambda name: MagicMock(cost=5) if name == "DummyObjectDetector" else None
        )

    @patch("eva.catalog.catalog_manager.CatalogManager.get_udf_cost_catalog_entry")
    def test_should_not_reorder_predicates(self, mock):
        def _check_no_reorder(cost_func):
            mock.side_effect = cost_func
            cheap_pred = "DummyObjectDetector(data).label = ['person']"
            costly_pred = "DummyMultiObjectDetector(data).labels @> ['person']"

            query = f"SELECT id FROM MyVideo WHERE {cheap_pred} AND {costly_pred};"
            plan = get_physical_query_plan(query)

            predicate_plans = list(plan.find_all(PredicatePlan))
            self.assertEqual(len(predicate_plans), 1)

            left: ComparisonExpression = predicate_plans[0].predicate.children[0]
            right: ComparisonExpression = predicate_plans[0].predicate.children[1]

            # predicates should not be reordered
            self.assertEqual(left.children[0].name, "DummyObjectDetector")
            self.assertEqual(right.children[0].name, "DummyMultiObjectDetector")

        # no reordering if first predicate has lower cost
        _check_no_reorder(
            lambda name: MagicMock(cost=10)
            if name == "DummyMultiObjectDetector"
            else MagicMock(cost=5)
        )

        # no reordering if both predicates have same cost
        _check_no_reorder(
            lambda name: MagicMock(cost=5)
            if name == "DummyMultiObjectDetector"
            else MagicMock(cost=5)
        )

        # no reordering if default cost is used for one UDF
        _check_no_reorder(
            lambda name: MagicMock(cost=5) if name == "DummyObjectDetector" else None
        )

        # no reordering if default cost is used for both UDF
        _check_no_reorder(lambda name: None)

    @patch("eva.catalog.catalog_manager.CatalogManager.get_udf_cost_catalog_entry")
    def test_should_reorder_multiple_predicates(self, mock):
        def side_effect_func(name):
            if name == "DummyMultiObjectDetector":
                return MagicMock(cost=10)
            else:
                return MagicMock(cost=5)

        mock.side_effect = side_effect_func

        chepeast_pred = "id<10"
        cheap_pred = "DummyObjectDetector(data).label = ['person']"
        costly_pred = "DummyMultiObjectDetector(data).labels @> ['person']"

        query = (
            f"SELECT id FROM MyVideo WHERE {costly_pred} AND {cheap_pred} AND "
            f"{chepeast_pred};"
        )

        plan = get_physical_query_plan(query)
        predicate_plans = list(plan.find_all(PredicatePlan))
        self.assertEqual(len(predicate_plans), 1)

        left = predicate_plans[0].predicate.children[0]
        right = predicate_plans[0].predicate.children[1]

        # only 2 comparison expressions as id predicate is pushed down
        self.assertIsInstance(left, ComparisonExpression)
        self.assertIsInstance(right, ComparisonExpression)
        # predicates reordered based on the cost
        self.assertEqual(left.children[0].name, "DummyObjectDetector")
        self.assertEqual(right.children[0].name, "DummyMultiObjectDetector")

    def test_reorder_rule_should_not_have_side_effects(self):
        query = "SELECT id FROM MyVideo WHERE id < 20 AND id > 10;"
        result = execute_query_fetch_all(query)

        with disable_rules([ReorderPredicates()]) as rules_manager:
            custom_plan_generator = PlanGenerator(rules_manager)
            expected = execute_query_fetch_all(
                query, plan_generator=custom_plan_generator
            )
            self.assertEqual(result, expected)
