# coding=utf-8
# Copyright 2018-2023 EvaDB
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
import gc
import os
import unittest
from pathlib import Path
from test.markers import gpu_skip_marker, windows_skip_marker
from test.util import (
    get_evadb_for_testing,
    get_logical_query_plan,
    load_functions_for_testing,
    shutdown_ray,
)

from mock import patch

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.models.storage.batch import Batch
from evadb.optimizer.operators import LogicalFunctionScan
from evadb.optimizer.plan_generator import PlanGenerator
from evadb.optimizer.rules.rules import (
    CacheFunctionExpressionInApply,
    CacheFunctionExpressionInFilter,
    CacheFunctionExpressionInProject,
)
from evadb.optimizer.rules.rules_manager import RulesManager, disable_rules
from evadb.server.command_handler import execute_query_fetch_all
from evadb.utils.stats import Timer


class ReuseTest(unittest.TestCase):
    def _load_hf_model(self):
        function_name = "HFObjectDetector"
        create_function_query = f"""CREATE FUNCTION {function_name}
            TYPE HuggingFace
            TASK 'object-detection'
            MODEL 'facebook/detr-resnet-50';
        """
        execute_query_fetch_all(self.evadb, create_function_query)

    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        ua_detrac = f"{EvaDB_ROOT_DIR}/data/ua_detrac/ua_detrac.mp4"
        execute_query_fetch_all(self.evadb, f"LOAD VIDEO '{ua_detrac}' INTO DETRAC;")
        execute_query_fetch_all(self.evadb, "CREATE TABLE fruitTable (data TEXT(100))")
        data_list = [
            "The color of apple is red",
            "The color of banana is yellow",
        ]
        for data in data_list:
            execute_query_fetch_all(
                self.evadb, f"INSERT INTO fruitTable (data) VALUES ('{data}')"
            )
        load_functions_for_testing(self.evadb)
        self._load_hf_model()

    def tearDown(self):
        shutdown_ray()
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS DETRAC;")
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS fruitTable;")

    def _verify_reuse_correctness(self, query, reuse_batch):
        # Fix memory failures on CI when running reuse test cases. An issue with yolo
        # surfaces when the system is running on low memory. Explicitly calling garbage
        # collection to reduce the memory usage.
        gc.collect()
        rules_manager = RulesManager(self.evadb.config)
        with disable_rules(
            rules_manager,
            [
                CacheFunctionExpressionInApply(),
                CacheFunctionExpressionInFilter(),
                CacheFunctionExpressionInProject(),
            ],
        ):
            custom_plan_generator = PlanGenerator(self.evadb, rules_manager)
            without_reuse_batch = execute_query_fetch_all(
                self.evadb, query, plan_generator=custom_plan_generator
            )

        self.assertEqual(reuse_batch.columns, reuse_batch.columns)
        reuse_batch.sort_orderby(by=[reuse_batch.columns[0]])
        without_reuse_batch.sort_orderby(by=[reuse_batch.columns[0]])
        # printing the batches so that we can see the mismatch in the logs
        self.assertEqual(
            without_reuse_batch,
            reuse_batch,
            msg=f"Without reuse {without_reuse_batch} \n With reuse{reuse_batch}",
        )

    def _reuse_experiment(self, queries):
        exec_times = []
        batches = []
        for query in queries:
            timer = Timer()
            with timer:
                batches.append(execute_query_fetch_all(self.evadb, query))
            exec_times.append(timer.total_elapsed_time)
        return batches, exec_times

    def _strict_reuse_experiment(self, queries):
        # This test mocks the apply_function_expression, if it is called, it will raise
        # an exception.
        exec_times = []
        batches = []
        for i, query in enumerate(queries):
            timer = Timer()
            if i != 0:
                with timer, patch.object(
                    Batch, "apply_function_expression"
                ) as mock_batch_func:
                    mock_batch_func.side_effect = Exception("Results are not reused")
                    batches.append(execute_query_fetch_all(self.evadb, query))
            else:
                with timer:
                    batches.append(execute_query_fetch_all(self.evadb, query))
            exec_times.append(timer.total_elapsed_time)
        return batches, exec_times

    def test_reuse_chatgpt(self):
        from evadb.constants import CACHEABLE_FUNCTIONS

        CACHEABLE_FUNCTIONS += ["DummyLLM"]
        select_query = """SELECT DummyLLM('What is the fruit described in this sentence', data)
            FROM fruitTable"""
        batches, exec_times = self._strict_reuse_experiment(
            [select_query, select_query]
        )
        self._verify_reuse_correctness(select_query, batches[1])
        self.assertTrue(exec_times[0] > exec_times[1])

    def test_reuse_when_query_is_duplicate(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL HFObjectDetector(data) AS Obj(score, label, bbox) WHERE id < 15;"""
        batches, exec_times = self._strict_reuse_experiment(
            [select_query, select_query]
        )
        self._verify_reuse_correctness(select_query, batches[1])
        self.assertTrue(exec_times[0] > exec_times[1])

    @gpu_skip_marker
    def test_reuse_partial(self):
        select_query1 = """SELECT id, label FROM DETRAC JOIN
            LATERAL HFObjectDetector(data) AS Obj(score, label, bbox) WHERE id < 5;"""
        select_query2 = """SELECT id, label FROM DETRAC JOIN
            LATERAL HFObjectDetector(data) AS Obj(score, label, bbox) WHERE id < 15;"""

        batches, exec_times = self._reuse_experiment([select_query1, select_query2])
        self._verify_reuse_correctness(select_query2, batches[1])

    @gpu_skip_marker
    def test_reuse_in_with_multiple_occurrences(self):
        select_query1 = """SELECT id, label FROM DETRAC JOIN
            LATERAL HFObjectDetector(data) AS Obj(score, label, bbox) WHERE id < 10;"""

        # multiple occurrences of the same function expression
        select_query2 = """SELECT id, HFObjectDetector(data).label FROM DETRAC JOIN
            LATERAL HFObjectDetector(data) AS Obj(score, label, bbox) WHERE id < 5;"""

        batches, exec_times = self._reuse_experiment([select_query1, select_query2])

        self._verify_reuse_correctness(select_query2, batches[1])

        # different query format
        select_query = (
            """SELECT id, HFObjectDetector(data).label FROM DETRAC WHERE id < 15;"""
        )
        reuse_batch = execute_query_fetch_all(self.evadb, select_query)
        self._verify_reuse_correctness(select_query, reuse_batch)

        # different query format
        select_query = """SELECT id, HFObjectDetector(data).label FROM DETRAC WHERE ['car'] <@ HFObjectDetector(data).label AND id < 20"""
        reuse_batch = execute_query_fetch_all(self.evadb, select_query)
        self._verify_reuse_correctness(select_query, reuse_batch)

    @gpu_skip_marker
    def test_reuse_logical_project_with_duplicate_query(self):
        project_query = (
            """SELECT id, HFObjectDetector(data).label FROM DETRAC WHERE id < 10;"""
        )
        batches, exec_times = self._reuse_experiment([project_query, project_query])
        self._verify_reuse_correctness(project_query, batches[1])
        # reuse should be faster than no reuse
        self.assertGreater(exec_times[0], exec_times[1])

    @gpu_skip_marker
    def test_reuse_with_function_in_predicate(self):
        select_query = """SELECT id FROM DETRAC WHERE ['car'] <@ HFObjectDetector(data).label AND id < 4"""

        batches, exec_times = self._reuse_experiment([select_query, select_query])
        self._verify_reuse_correctness(select_query, batches[1])
        # reuse should be faster than no reuse
        self.assertGreater(exec_times[0], exec_times[1])

    @gpu_skip_marker
    def test_reuse_across_different_predicate_using_same_function(self):
        query1 = """SELECT id FROM DETRAC WHERE ['car'] <@ HFObjectDetector(data).label AND id < 15"""

        query2 = """SELECT id FROM DETRAC WHERE ArrayCount(HFObjectDetector(data).label, 'car') > 3 AND id < 12;"""

        batches, exec_times = self._reuse_experiment([query1, query2])
        self._verify_reuse_correctness(query2, batches[1])
        # reuse should be faster than no reuse
        self.assertGreater(exec_times[0], exec_times[1])

    @gpu_skip_marker
    def test_reuse_filter_with_project(self):
        project_query = """
            SELECT id, Yolo(data).labels FROM DETRAC WHERE id < 5;"""
        select_query = """
            SELECT id FROM DETRAC
            WHERE ArrayCount(Yolo(data).labels, 'car') > 3 AND id < 5;"""
        batches, exec_times = self._reuse_experiment([project_query, select_query])
        self._verify_reuse_correctness(select_query, batches[1])
        # reuse should be faster than no reuse
        self.assertGreater(exec_times[0], exec_times[1])

    @gpu_skip_marker
    def test_reuse_in_extract_object(self):
        select_query = """
            SELECT id, T.iids, T.bboxes, T.scores, T.labels
            FROM DETRAC JOIN LATERAL EXTRACT_OBJECT(data, Yolo, NorFairTracker)
                AS T(iids, labels, bboxes, scores)
            WHERE id < 30;
            """
        batches, exec_times = self._reuse_experiment([select_query, select_query])
        self._verify_reuse_correctness(select_query, batches[1])
        self.assertGreater(exec_times[0], exec_times[1])

    @windows_skip_marker
    def test_reuse_after_server_shutdown(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL Yolo(data) AS Obj(label, bbox, conf) WHERE id < 4;"""
        execute_query_fetch_all(self.evadb, select_query)

        # Stop and restart server
        os.system("nohup evadb_server --stop")
        os.system("nohup evadb_server --start &")

        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL Yolo(data) AS Obj(label, bbox, conf) WHERE id < 6;"""

        reuse_batch = execute_query_fetch_all(self.evadb, select_query)
        self._verify_reuse_correctness(select_query, reuse_batch)

        # stop the server
        os.system("nohup evadb_server --stop")

    def test_drop_function_should_remove_cache(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL Yolo(data) AS Obj(label, bbox, conf) WHERE id < 5;"""
        execute_query_fetch_all(self.evadb, select_query)

        plan = next(
            get_logical_query_plan(self.evadb, select_query).find_all(
                LogicalFunctionScan
            )
        )
        cache_name = plan.func_expr.signature()

        # cache exists
        function_cache = self.evadb.catalog().get_function_cache_catalog_entry_by_name(
            cache_name
        )
        cache_dir = Path(function_cache.cache_path)
        self.assertIsNotNone(function_cache)
        self.assertTrue(cache_dir.exists())

        # cache should be removed if the FUNCTION is removed
        execute_query_fetch_all(self.evadb, "DROP FUNCTION Yolo;")
        function_cache = self.evadb.catalog().get_function_cache_catalog_entry_by_name(
            cache_name
        )
        self.assertIsNone(function_cache)
        self.assertFalse(cache_dir.exists())

    def test_drop_table_should_remove_cache(self):
        select_query = """SELECT id, label FROM DETRAC JOIN
            LATERAL Yolo(data) AS Obj(label, bbox, conf) WHERE id < 5;"""
        execute_query_fetch_all(self.evadb, select_query)

        plan = next(
            get_logical_query_plan(self.evadb, select_query).find_all(
                LogicalFunctionScan
            )
        )
        cache_name = plan.func_expr.signature()

        # cache exists
        function_cache = self.evadb.catalog().get_function_cache_catalog_entry_by_name(
            cache_name
        )
        cache_dir = Path(function_cache.cache_path)
        self.assertIsNotNone(function_cache)
        self.assertTrue(cache_dir.exists())

        # cache should be removed if the Table is removed
        execute_query_fetch_all(self.evadb, "DROP TABLE DETRAC;")
        function_cache = self.evadb.catalog().get_function_cache_catalog_entry_by_name(
            cache_name
        )
        self.assertIsNone(function_cache)
        self.assertFalse(cache_dir.exists())
