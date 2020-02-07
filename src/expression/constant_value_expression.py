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
    ExpressionType


class ConstantValueExpression(AbstractExpression):
    # ToDo Implement generic value class
    # for now we don't assign any class to value
    # it can have types like string, int etc
    # return type not set, handle that based on value
    def __init__(self, value):
        super().__init__(ExpressionType.CONSTANT_VALUE)
        self._value = value

    def evaluate(self, *args):
        return self._value

    @property
    def value(self):
        return self._value
    # ToDo implement other functinalities like maintaining hash
    # comparing two objects of this class(==)
