# coding=utf-8
# Copyright 2018-2020 EVA
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
from src.optimizer.operators import LogicalProject, LogicalGet, \
    LogicalFilter, LogicalInsert, Operator, LogicalCreateUDF, LogicalLoadData
from src.optimizer.plan_generator import PlanGenerator
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.comparison_expression import ComparisonExpression
from src.expression.function_expression import FunctionExpression
from src.expression.abstract_expression import ExpressionType
from src.expression.logical_expression import LogicalExpression
from src.catalog.catalog_manager import CatalogManager
from test.util import (create_sample_video, NUM_FRAMES,
                       perform_query, DummyObjectDetector)
from src.models.storage.batch import Batch
import os
import pandas as pd


class CascadeOptimizer(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)

    def tearDown(self):
        os.remove('dummy.avi')

    def test_plan(self):
        logical_get = LogicalGet("dummy", None)
        const_exp1 = ConstantValueExpression(1)
        const_exp2 = ConstantValueExpression(0)
        const_exp3 = ConstantValueExpression(0)
        func_expr = FunctionExpression(lambda x: x+1)
        cmpr_exp1 = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            const_exp1,
            const_exp2
        )
        cmpr_exp2 = ComparisonExpression(
            ExpressionType.COMPARE_GREATER,
            func_expr,
            const_exp3
        )

        and_expr = LogicalExpression(
            ExpressionType.LOGICAL_AND, cmpr_exp2, cmpr_exp1)

        logical_filter = LogicalFilter(and_expr, None)
        logical_project = LogicalProject(["id1", "id2"], None)
        logical_project.append_child(logical_filter)
        logical_filter.append_child(logical_get)

        PlanGenerator().build(logical_project)

    def test_logical_to_physical_udf(self):
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        perform_query(load_query)

        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY (3, 256, 256))
                  OUTPUT (label TEXT(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        perform_query(create_udf_query)

        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE Classification(data).label = 'person';"
        actual_batch = perform_query(select_query)
        actual_batch.sort()
        expected = [{'id': i * 2, 'label': 'person'}
                    for i in range(NUM_FRAMES // 2)]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)


if __name__ == "__main__":
    unittest.main()
