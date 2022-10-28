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
        vl = self.get_child(0).evaluate(*args, **kwargs)
        vr = self.get_child(1).evaluate(*args, **kwargs)

        return Batch.combine_batches(vl, vr, self.etype)

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, ArithmeticExpression):
            return False
        return is_subtree_equal and self.etype == other.etype
