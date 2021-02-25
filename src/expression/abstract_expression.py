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
from abc import ABC, abstractmethod
from enum import IntEnum, unique

from src.utils import generic_utils


@unique
class ExpressionType(IntEnum):
    INVALID = 0,
    CONSTANT_VALUE = 1,
    TUPLE_VALUE = 2,
    # Compare operators
    COMPARE_EQUAL = 3,
    COMPARE_GREATER = 4,
    COMPARE_LESSER = 5,
    COMPARE_GEQ = 6,
    COMPARE_LEQ = 7,
    COMPARE_NEQ = 8,
    # Logical operators
    LOGICAL_AND = 9,
    LOGICAL_OR = 10,
    LOGICAL_NOT = 11,
    # Arithmetic operators
    ARITHMETIC_ADD = 12,
    ARITHMETIC_SUBTRACT = 13,
    ARITHMETIC_MULTIPLY = 14,
    ARITHMETIC_DIVIDE = 15,

    FUNCTION_EXPRESSION = 16,

    AGGREGATION_COUNT = 17,
    AGGREGATION_SUM = 18,
    AGGREGATION_MIN = 19,
    AGGREGATION_MAX = 20,
    AGGREGATION_AVG = 21,

    CASE = 22,
    # add other types


@unique
class ExpressionReturnType(IntEnum):
    INVALID = 0,
    BOOLEAN = 1,
    INTEGER = 2,
    VARCHAR = 3,
    FLOAT = 4,
    # add others


class AbstractExpression(ABC):

    def __init__(self, exp_type: ExpressionType, **kwargs):
        allowed_kwargs = {
            'rtype',
            'children'
        }
        generic_utils.validate_kwargs(kwargs, allowed_kwargs)
        self._etype = exp_type
        self._rtype = kwargs.get('rtype', ExpressionReturnType.INVALID)
        self._children = kwargs.get('children', [])
        self._predicates = []

    def get_child(self, index: int):
        if index < 0 or index >= len(self._children):
            return None
        else:
            return self._children[index]

    @property
    def children(self):
        return self._children

    def append_child(self, child):
        self._children.append(child)

    def get_children_count(self) -> int:
        return len(self._children)

    @property
    def etype(self) -> ExpressionType:
        return self._etype

    @etype.setter
    def etype(self, expr_type: ExpressionType):
        self._etype = expr_type

    @property
    # def predicates(self) -> List[Predicate]:
    def predicates(self):
        return self._predicates

    def clear_predicates(self):
        self._predicates.clear()

    def get_predicate_count(self) -> int:
        return len(self._predicates)

    @property
    def return_type(self) -> ExpressionReturnType:
        return self._return_type

    @return_type.setter
    def return_type(self, return_type: ExpressionReturnType):
        self._return_type = return_type

    # todo define a generic return type for this function
    # not sure if we should keep tuple1, tuple2 explicitly
    # since not many sub-classes are using both tuples
    # how about if we maintain *args
    # refactor if need be
    @abstractmethod
    def evaluate(self, *args):
        NotImplementedError('Must be implemented in subclasses.')

    def __eq__(self, other):
        is_subtree_equal = True
        if not isinstance(other, AbstractExpression):
            return False
        if self.get_children_count() != other.get_children_count():
            return False
        for child1, child2 in zip(self.children, other.children):
            is_subtree_equal = is_subtree_equal and (child1 == child2)
        return is_subtree_equal
