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
from test.util import load_inbuilt_udfs

from mock import patch

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.rules.rules import (
    PushDownFilterThroughApplyAndMerge,
    PushDownFilterThroughJoin,
    XformLateralJoinToLinearFlow,
)
from eva.optimizer.rules.rules_manager import disable_rules
from eva.server.command_handler import execute_query_fetch_all
from eva.utils.timer import Timer


class OptimizerRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        ua_detrac = f"{EVA_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{ua_detrac}' INTO MyVideo;")
        load_inbuilt_udfs()

    @classmethod
    def tearDownClass(cls):
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
