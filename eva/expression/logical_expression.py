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


class LogicalExpression(AbstractExpression):
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
        if self.get_children_count() == 2:

            left_batch = self.get_child(0).evaluate(*args, **kwargs)
            if self.etype == ExpressionType.LOGICAL_AND:

                if left_batch.all_false():  # check if all are false
                    return left_batch
                kwargs["mask"] = left_batch.create_mask()
            elif self.etype == ExpressionType.LOGICAL_OR:
                if left_batch.all_true():  # check if all are true
                    return left_batch
                kwargs["mask"] = left_batch.create_inverted_mask()
            right_batch = self.get_child(1).evaluate(*args, **kwargs)
            left_batch.update_indices(kwargs["mask"], right_batch)

            return left_batch
        else:
            batch = self.get_child(0).evaluate(*args, **kwargs)
            if self.etype == ExpressionType.LOGICAL_NOT:
                batch.invert()
                return batch

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, LogicalExpression):
            return False
        return is_subtree_equal and self.etype == other.etype

    def __hash__(self) -> int:
        return super().__hash__()
