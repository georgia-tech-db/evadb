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

import pandas as pd

from src.expression.abstract_expression import ExpressionType
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.function_expression import FunctionExpression
from src.models.inference.outcome import Outcome
from src.models.storage.batch import Batch

from test.util import create_dataframe


class ExpressionEvaluationTest(unittest.TestCase):
    def test_func_expr_with_cmpr_and_const_expr_should_work(self):
        frames = create_dataframe(2)
        outcome_1 = Outcome(pd.DataFrame(
            {'labels': ["car", "bus"], 'scores': [0.5, 0.6]}), 'labels')
        outcome_2 = Outcome(pd.DataFrame(
            {'labels': ["bus"], 'scores': [0.6]}), 'labels')

        func = FunctionExpression(lambda x: [outcome_1, outcome_2])
        value_expr = ConstantValueExpression("car")
        expression_tree = ComparisonExpression(ExpressionType.COMPARE_EQUAL,
                                               func,
                                               value_expr)

        batch = Batch(frames=frames)

        self.assertEqual([True, False], expression_tree.evaluate(batch))
