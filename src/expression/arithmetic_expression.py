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
    ExpressionType, ExpressionReturnType


class ArithmeticExpression(AbstractExpression):

    def __init__(self, exp_type: ExpressionType, left: AbstractExpression,
                 right: AbstractExpression):
        children = []
        if left is not None:
            children.append(left)
        if right is not None:
            children.append(right)
        super().__init__(exp_type, rtype=ExpressionReturnType.FLOAT,
                         children=children)

    def evaluate(self, *args):
        vl = self.get_child(0).evaluate(*args)
        vr = self.get_child(1).evaluate(*args)

        if (self.etype == ExpressionType.ARITHMETIC_ADD):
            return vl + vr
        elif(self.etype == ExpressionType.ARITHMETIC_SUBTRACT):
            return vl - vr
        elif(self.etype == ExpressionType.ARITHMETIC_MULTIPLY):
            return vl * vr
        elif(self.etype == ExpressionType.ARITHMETIC_DIVIDE):
            return vl / vr
