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
from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType, \
    ExpressionReturnType
from src.models.storage.batch import Batch
import pandas as pd
import numpy as np


class ComparisonExpression(AbstractExpression):
    def __init__(self, exp_type: ExpressionType, left: AbstractExpression,
                 right: AbstractExpression):
        children = []
        if left is not None:
            children.append(left)
        if right is not None:
            children.append(right)
        super().__init__(exp_type, rtype=ExpressionReturnType.BOOLEAN,
                         children=children)

    def evaluate(self, *args, **kwargs):
        # evaluate always return batch
        left_values = self.get_child(0).evaluate(*args, **kwargs).frames
        right_values = self.get_child(1).evaluate(*args, **kwargs).frames

        if len(left_values) != len(right_values):
            if len(left_values) == 1:
                left_values = pd.DataFrame(np.repeat(left_values.values,
                                                     len(right_values),
                                                     axis=0))
            elif len(right_values) == 1:
                right_values = pd.DataFrame(np.repeat(right_values.values,
                                                      len(left_values),
                                                      axis=0))
            else:
                raise Exception(
                    "Left and Right batch does not have equal elements")

        if self.etype == ExpressionType.COMPARE_EQUAL:
            return Batch(pd.DataFrame(
                left_values.values == right_values.values))
        elif self.etype == ExpressionType.COMPARE_GREATER:
            return Batch(pd.DataFrame(
                left_values.values > right_values.values))
        elif self.etype == ExpressionType.COMPARE_LESSER:
            return Batch(pd.DataFrame(
                left_values.values < right_values.values))
        elif self.etype == ExpressionType.COMPARE_GEQ:
            return Batch(pd.DataFrame(
                left_values.values >= right_values.values))
        elif self.etype == ExpressionType.COMPARE_LEQ:
            return Batch(pd.DataFrame(
                left_values.values <= right_values.values))
        elif self.etype == ExpressionType.COMPARE_NEQ:
            return Batch(pd.DataFrame(
                left_values.values != right_values.values))

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, ComparisonExpression):
            return False
        return (is_subtree_equal
                and self.etype == other.etype)
