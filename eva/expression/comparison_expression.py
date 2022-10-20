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


class ComparisonExpression(AbstractExpression):
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
            exp_type, rtype=ExpressionReturnType.BOOLEAN, children=children
        )

    def evaluate(self, *args, **kwargs):
        # cast in to numpy array
        lbatch = self.get_child(0).evaluate(*args, **kwargs)
        rbatch = self.get_child(1).evaluate(*args, **kwargs)

        if len(lbatch) != len(rbatch):
            if len(lbatch) == 1:
                lbatch.repeat(len(rbatch))
            elif len(rbatch) == 1:
                rbatch.repeat(len(lbatch))
            else:
                raise Exception("Left and Right batch does not have equal elements")

        if self.etype == ExpressionType.COMPARE_EQUAL:
            return Batch.from_eq(lbatch, rbatch)
        elif self.etype == ExpressionType.COMPARE_GREATER:
            return Batch.from_greater(lbatch, rbatch)
        elif self.etype == ExpressionType.COMPARE_LESSER:
            return Batch.from_lesser(lbatch, rbatch)
        elif self.etype == ExpressionType.COMPARE_GEQ:
            return Batch.from_greater_eq(lbatch, rbatch)
        elif self.etype == ExpressionType.COMPARE_LEQ:
            return Batch.from_lesser_eq(lbatch, rbatch)
        elif self.etype == ExpressionType.COMPARE_NEQ:
            return Batch.from_not_eq(lbatch, rbatch)
        elif self.etype == ExpressionType.COMPARE_CONTAINS:
            return Batch.compare_contains(lbatch, rbatch)
        elif self.etype == ExpressionType.COMPARE_IS_CONTAINED:
            return Batch.compare_is_contained(lbatch, rbatch)
        else:
            raise NotImplementedError

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, ComparisonExpression):
            return False
        return is_subtree_equal and self.etype == other.etype

    def __hash__(self) -> int:
        return super().__hash__()
