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
        batch: Batch = self.get_child(0).evaluate(*args, **kwargs)
        if self.etype == ExpressionType.AGGREGATION_FIRST:
            batch = batch[0]
        elif self.etype == ExpressionType.AGGREGATION_LAST:
            batch = batch[-1]
        elif self.etype == ExpressionType.AGGREGATION_SEGMENT:
            batch = Batch.stack(batch)
        elif self.etype == ExpressionType.AGGREGATION_SUM:
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

        column_name = self.etype.name
        if column_name.find("AGGREGATION_") != -1:
            # AGGREGATION_MAX -> MAX
            updated_column_name = column_name.replace("AGGREGATION_", "")
            batch.modify_column_alias(updated_column_name)

        # TODO: Raise exception if data type doesn't match
        return batch

    def get_symbol(self) -> str:

        if self.etype == ExpressionType.AGGREGATION_FIRST:
            return "FIRST"
        if self.etype == ExpressionType.AGGREGATION_LAST:
            return "LAST"
        if self.etype == ExpressionType.AGGREGATION_SEGMENT:
            return "SEGMENT"
        if self.etype == ExpressionType.AGGREGATION_SUM:
            return "SUM"
        elif self.etype == ExpressionType.AGGREGATION_COUNT:
            return "COUNT"
        elif self.etype == ExpressionType.AGGREGATION_AVG:
            return "AVG"
        elif self.etype == ExpressionType.AGGREGATION_MIN:
            return "MIN"
        elif self.etype == ExpressionType.AGGREGATION_MAX:
            return "MAX"
        else:
            raise NotImplementedError

    def signature(self) -> str:
        child_sigs = []
        for child in self.children:
            child_sigs.append(child.signature())
        return f"{self.get_symbol().lower()}({','.join(child_sigs)})"

    def __str__(self) -> str:
        expr_str = ""
        if self.etype:
            expr_str = f"{str(self.get_symbol())}()"
        return expr_str

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
