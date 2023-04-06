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
import os
import unittest
from pathlib import Path
from test.markers import windows_skip_marker
from test.util import get_logical_query_plan, load_udfs_for_testing, shutdown_ray

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.expression.function_expression import FunctionExpression
from eva.optimizer.operators import LogicalFilter, LogicalFunctionScan
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.rules.rules import CacheFunctionExpressionInApply
from eva.optimizer.rules.rules_manager import disable_rules
from eva.server.command_handler import execute_query_fetch_all
from eva.utils.stats import Timer


class ReuseTest(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        ua_detrac = f"{EVA_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        execute_query_fetch_all(f"LOAD VIDEO '{ua_detrac}' INTO DETRAC;")
        load_udfs_for_testing()

    def tearDown(self):
        shutdown_ray()
        execute_query_fetch_all("DROP TABLE IF EXISTS DETRAC;")

    def _verify_reuse_correctness(self, query, reuse_batch):
        with disable_rules([CacheFunctionExpressionInApply()]) as rules_manager:
            custom_plan_generator = PlanGenerator(rules_manager)
            without_reuse_batch = execute_query_fetch_all(
                query, plan_generator=custom_plan_generator
            )
        self.assertEqual(without_reuse_batch, reuse_batch)

    def test_reuse_when_query_is_duplicate(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 15;"""
        no_reuse_timer = Timer()
        reuse_timer = Timer()

        with no_reuse_timer:
            execute_query_fetch_all(select_query)
        with reuse_timer:
            reuse_batch = execute_query_fetch_all(select_query)

        self._verify_reuse_correctness(select_query, reuse_batch)

        # reuse should be faster than no reuse
        self.assertTrue(
            no_reuse_timer.total_elapsed_time > reuse_timer.total_elapsed_time
        )

    def test_reuse_partial(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 5;"""

        execute_query_fetch_all(select_query)
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 15;"""

        reuse_batch = execute_query_fetch_all(select_query)
        self._verify_reuse_correctness(select_query, reuse_batch)

    def test_reuse_in_with_multiple_occurences(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 10;"""

        execute_query_fetch_all(select_query)

        # multiple occurences of the same function expression
        select_query = """SELECT id, YoloV5(data).labels FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 15;"""

        reuse_batch = execute_query_fetch_all(select_query)
        self._verify_reuse_correctness(select_query, reuse_batch)

        # enable these test cases when we increase the support of caching
        if False:
            # different query format
            select_query = (
                """SELECT id, YoloV5(data).labels FROM DETRAC WHERE id < 25;"""
            )
            reuse_batch = execute_query_fetch_all(select_query)
            self._verify_reuse_correctness(select_query, reuse_batch)

            # different query format
            select_query = """SELECT id, YoloV5(data).scores FROM DETRAC WHERE ['car'] <@ YoloV5(data).labels AND id < 20"""
            reuse_batch = execute_query_fetch_all(select_query)
            self._verify_reuse_correctness(select_query, reuse_batch)

    def test_reuse_does_not_work_when_expression_in_where_clause(self):
        # add with subsequent PR
        select_query = """
            SELECT id FROM DETRAC
            WHERE ArrayCount(YoloV5(data).labels, 'car') > 3 AND id < 5;"""
        plan = next(get_logical_query_plan(select_query).find_all(LogicalFilter))
        yolo_expr = None
        for expr in plan.predicate.find_all(FunctionExpression):
            if expr.name == "YoloV5":
                yolo_expr = expr

        self.assertFalse(yolo_expr.has_cache())

    @windows_skip_marker
    def test_reuse_after_server_shutdown(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 10;"""
        execute_query_fetch_all(select_query)

        # Stop and restart server
        os.system("nohup eva_server --stop")
        os.system("nohup eva_server --start &")

        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 15;"""

        reuse_batch = execute_query_fetch_all(select_query)
        self._verify_reuse_correctness(select_query, reuse_batch)

        # stop the server
        os.system("nohup eva_server --stop")

    def test_drop_udf_should_remove_cache(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 5;"""
        execute_query_fetch_all(select_query)

        plan = next(get_logical_query_plan(select_query).find_all(LogicalFunctionScan))
        cache_name = plan.func_expr.signature()
        catalog_manager = CatalogManager()

        # cache exists
        udf_cache = catalog_manager.get_udf_cache_catalog_entry_by_name(cache_name)
        cache_dir = Path(udf_cache.cache_path)
        self.assertIsNotNone(udf_cache)
        self.assertTrue(cache_dir.exists())

        # cache should be removed if the UDF is removed
        execute_query_fetch_all("DROP UDF YoloV5;")
        udf_cache = catalog_manager.get_udf_cache_catalog_entry_by_name(cache_name)
        self.assertIsNone(udf_cache)
        self.assertFalse(cache_dir.exists())

    def test_drop_table_should_remove_cache(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 5;"""
        execute_query_fetch_all(select_query)

        plan = next(get_logical_query_plan(select_query).find_all(LogicalFunctionScan))
        cache_name = plan.func_expr.signature()
        catalog_manager = CatalogManager()

        # cache exists
        udf_cache = catalog_manager.get_udf_cache_catalog_entry_by_name(cache_name)
        cache_dir = Path(udf_cache.cache_path)
        self.assertIsNotNone(udf_cache)
        self.assertTrue(cache_dir.exists())

        # cache should be removed if the Table is removed
        execute_query_fetch_all("DROP TABLE DETRAC;")
        udf_cache = catalog_manager.get_udf_cache_catalog_entry_by_name(cache_name)
        self.assertIsNone(udf_cache)
        self.assertFalse(cache_dir.exists())
