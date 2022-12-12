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
from eva.expression.abstract_expression import (
    AbstractExpression,
    ExpressionReturnType,
    ExpressionType,
)
from eva.models.storage.batch import Batch


class AggregationExpression(AbstractExpression):
    def __init__(
        self,
        exp_type: ExpressionType,
        left: AbstractExpression,
        right: AbstractExpression,
    ):
        children = []
        if left is not None:
            children.append(left)
        if right is not None:
            children.append(right)
        super().__init__(
            exp_type, rtype=ExpressionReturnType.INTEGER, children=children
        )  # can also be a float

    def evaluate(self, *args, **kwargs):
        batch = self.get_child(0).evaluate(*args, **kwargs)
        if self.etype == ExpressionType.AGGREGATION_FIRST:
            batch = batch[0]
        if self.etype == ExpressionType.AGGREGATION_LAST:
            batch = batch[-1]
        if self.etype == ExpressionType.AGGREGATION_SEGMENT:
            batch = Batch.stack(batch)
        if self.etype == ExpressionType.AGGREGATION_SUM:
            batch.aggregate("sum")
        elif self.etype == ExpressionType.AGGREGATION_COUNT:
            batch.aggregate("count")
        elif self.etype == ExpressionType.AGGREGATION_AVG:
            batch.aggregate("mean")
        elif self.etype == ExpressionType.AGGREGATION_MIN:
            batch.aggregate("min")
        elif self.etype == ExpressionType.AGGREGATION_MAX:
            batch.aggregate("max")
        batch.reset_index()
        # TODO ACTION:
        # Add raise exception if data type doesn't match

        return batch

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, AggregationExpression):
            return False
        return is_subtree_equal and self.etype == other.etype

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.etype,
            )
        )
