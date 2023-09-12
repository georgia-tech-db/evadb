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
import unittest

import pandas as pd

from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.models.storage.batch import Batch


class ConstantExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_constant_with_input_relationship(self):
        const_expr = ConstantValueExpression(1)
        input_size = 10
        self.assertEqual(
            [1] * input_size,
            const_expr.evaluate(Batch(pd.DataFrame([0] * input_size)))
            .frames[0]
            .tolist(),
        )
