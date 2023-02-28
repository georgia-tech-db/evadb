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
from pathlib import Path
from test.util import get_logical_query_plan, load_inbuilt_udfs

from eva.catalog.catalog_manager import CatalogManager
from eva.optimizer.operators import LogicalFunctionScan
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.rules.rules import CacheFunctionExpressionInApply
from eva.optimizer.rules.rules_manager import disable_rules
from eva.server.command_handler import execute_query_fetch_all


class ReuseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CatalogManager().reset()
        load_query = """LOAD VIDEO './data/ua_detrac/ua_detrac.mp4' INTO DETRAC;"""
        execute_query_fetch_all(load_query)
        load_inbuilt_udfs()

    @classmethod
    def tearDownClass(cls):
        execute_query_fetch_all("DROP TABLE IF EXISTS DETRAC;")

    def test_reuse(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 5;"""

        execute_query_fetch_all(select_query)
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL YoloV5(data) AS Obj(label, bbox, conf) WHERE id < 15;"""

        reuse_batch = execute_query_fetch_all(select_query)

        with disable_rules([CacheFunctionExpressionInApply()]) as rules_manager:
            custom_plan_generator = PlanGenerator(rules_manager)
            without_reuse_batch = execute_query_fetch_all(
                select_query, plan_generator=custom_plan_generator
            )
        self.assertEqual(without_reuse_batch, reuse_batch)

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

        # cache should be removed if the UDF is removed
        execute_query_fetch_all("DROP TABLE DETRAC;")
        udf_cache = catalog_manager.get_udf_cache_catalog_entry_by_name(cache_name)
        self.assertIsNone(udf_cache)
        self.assertFalse(cache_dir.exists())
