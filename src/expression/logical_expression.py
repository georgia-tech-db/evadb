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
import pandas as pd
from src.models.storage.batch import Batch


class LogicalExpression(AbstractExpression):
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
        if self.get_children_count() == 2:
            left_values = self.get_child(0).evaluate(*args, **kwargs).frames
            if self.etype == ExpressionType.LOGICAL_AND:
                if (~left_values).all().bool():  # check if all are false
                    return Batch(left_values)
                kwargs["mask"] = left_values[left_values[0]].index.tolist()
            elif self.etype == ExpressionType.LOGICAL_OR:
                if left_values.all().bool():  # check if all are true
                    return Batch(left_values)
                kwargs["mask"] = left_values[~left_values[0]].index.tolist()
            right_values = self.get_child(
                1).evaluate(*args, **kwargs).frames
            left_values.iloc[kwargs["mask"]] = right_values
            return Batch(pd.DataFrame(left_values))
        else:
            values = self.get_child(0).evaluate(*args, **kwargs).frames
            if self.etype == ExpressionType.LOGICAL_NOT:
                return Batch(pd.DataFrame(~values))

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalExpression):
            return False
        return (is_subtree_equal
                and self.etype == other.etype)
