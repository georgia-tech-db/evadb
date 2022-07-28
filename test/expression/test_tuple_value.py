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

import pandas as pd

from eva.expression.tuple_value_expression import TupleValueExpression
from eva.models.storage.batch import Batch


class TupleValueExpressionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_masking(self):
        tup_val_exp1 = TupleValueExpression(col_name=0)
        tup_val_exp2 = TupleValueExpression(col_name=1)
        tup_val_exp3 = TupleValueExpression(col_name=2)
        tup_val_exp1.col_alias = 0
        tup_val_exp2.col_alias = 1
        tup_val_exp3.col_alias = 2
        tuples = Batch(
            pd.DataFrame(
                {
                    0: [1, 2, 3, 4, 5, 6],
                    1: [7, 8, 9, 10, 11, 12],
                    2: [13, 14, 15, 16, 17, 18],
                }
            )
        )
        mask1 = [0, 1, 2, 3, 4, 5]
        self.assertEqual(
            [1, 2, 3, 4, 5, 6],
            tup_val_exp1.evaluate(tuples, mask=mask1).frames[0].tolist(),
        )
        self.assertEqual(
            [7, 9, 11], tup_val_exp2.evaluate(tuples, mask=[0, 2, 4]).frames[1].tolist()
        )
        self.assertEqual([], tup_val_exp3.evaluate(tuples, mask=[]).frames[2].tolist())
