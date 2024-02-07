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

from evadb.expression.abstract_expression import (
    AbstractExpression,
    ExpressionReturnType,
    ExpressionType,
)
from evadb.models.storage.batch import Batch


class ArithmeticExpression(AbstractExpression):
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
        super().__init__(exp_type, rtype=ExpressionReturnType.FLOAT, children=children)

    def evaluate(self, *args, **kwargs):
        lbatch = self.get_child(0).evaluate(*args, **kwargs)
        rbatch = self.get_child(1).evaluate(*args, **kwargs)

        assert len(lbatch) == len(
            rbatch
        ), f"Left and Right batch does not have equal elements: left: {len(lbatch)} right: {len(rbatch)}"

        assert self.etype in [
            ExpressionType.ARITHMETIC_ADD,
            ExpressionType.ARITHMETIC_SUBTRACT,
            ExpressionType.ARITHMETIC_DIVIDE,
            ExpressionType.ARITHMETIC_MULTIPLY,
            ExpressionType.ARITHMETIC_MODULUS,
        ], f"Expression type not supported {self.etype}"

        if self.etype == ExpressionType.ARITHMETIC_ADD:
            return Batch.from_add(lbatch, rbatch)
        elif self.etype == ExpressionType.ARITHMETIC_SUBTRACT:
            return Batch.from_subtract(lbatch, rbatch)
        elif self.etype == ExpressionType.ARITHMETIC_MULTIPLY:
            return Batch.from_multiply(lbatch, rbatch)
        elif self.etype == ExpressionType.ARITHMETIC_DIVIDE:
            return Batch.from_divide(lbatch, rbatch)
        elif self.etype == ExpressionType.ARITHMETIC_MODULUS:
            return Batch.from_modulus(lbatch, rbatch)

        return Batch.combine_batches(lbatch, rbatch, self.etype)

    def get_symbol(self) -> str:
        if self.etype == ExpressionType.ARITHMETIC_ADD:
            return "+"
        elif self.etype == ExpressionType.ARITHMETIC_SUBTRACT:
            return "-"
        elif self.etype == ExpressionType.ARITHMETIC_MULTIPLY:
            return "*"
        elif self.etype == ExpressionType.ARITHMETIC_DIVIDE:
            return "/"
        elif self.etype == ExpressionType.ARITHMETIC_MODULUS:
            return "%"

    def __str__(self) -> str:
        expr_str = "("
        if self.get_child(0):
            expr_str += f"{self.get_child(0)}"
        if self.etype:
            expr_str += f" {self.get_symbol()} "
        if self.get_child(1):
            expr_str += f"{self.get_child(1)}"
        expr_str += ")"
        return expr_str

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, ArithmeticExpression):
            return False
        return is_subtree_equal and self.etype == other.etype

    def __hash__(self) -> int:
        return super().__hash__()
