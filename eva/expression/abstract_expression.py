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
from abc import ABC, abstractmethod
from enum import IntEnum, auto, unique


@unique
class ExpressionType(IntEnum):
    INVALID = auto()
    CONSTANT_VALUE = auto()
    TUPLE_VALUE = auto()
    # Compare operators
    COMPARE_EQUAL = auto()
    COMPARE_GREATER = auto()
    COMPARE_LESSER = auto()
    COMPARE_GEQ = auto()
    COMPARE_LEQ = auto()
    COMPARE_NEQ = auto()
    COMPARE_CONTAINS = auto()
    COMPARE_IS_CONTAINED = auto()
    # Logical operators
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()
    LOGICAL_NOT = auto()
    # Arithmetic operators
    ARITHMETIC_ADD = auto()
    ARITHMETIC_SUBTRACT = auto()
    ARITHMETIC_MULTIPLY = auto()
    ARITHMETIC_DIVIDE = auto()

    FUNCTION_EXPRESSION = auto()

    AGGREGATION_COUNT = auto()
    AGGREGATION_SUM = auto()
    AGGREGATION_MIN = auto()
    AGGREGATION_MAX = auto()
    AGGREGATION_AVG = auto()
    AGGREGATION_FIRST = auto()
    AGGREGATION_LAST = auto()
    AGGREGATION_SEGMENT = auto()

    CASE = auto()
    # add other types


@unique
class ExpressionReturnType(IntEnum):
    INVALID = auto()
    BOOLEAN = auto()
    INTEGER = auto()
    VARCHAR = auto()
    FLOAT = auto()
    # add others


class AbstractExpression(ABC):
    def __init__(
        self,
        exp_type: ExpressionType,
        rtype: ExpressionReturnType = ExpressionReturnType.INVALID,
        children=None,
    ):
        self._etype = exp_type
        self._rtype = rtype
        self._children = children or []

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
    def rtype(self) -> ExpressionReturnType:
        return self._rtype

    @rtype.setter
    def r_type(self, rtype: ExpressionReturnType):
        self._rtype = rtype

    # todo define a generic return type for this function
    # not sure if we should keep tuple1, tuple2 explicitly
    # since not many sub-classes are using both tuples
    # how about if we maintain *args
    # refactor if need be
    @abstractmethod
    def evaluate(self, *args, **kwargs):
        NotImplementedError("Must be implemented in subclasses.")

    def __eq__(self, other):
        is_subtree_equal = True
        if not isinstance(other, AbstractExpression):
            return False
        if self.get_children_count() != other.get_children_count():
            return False
        for child1, child2 in zip(self.children, other.children):
            is_subtree_equal = is_subtree_equal and (child1 == child2)
        return is_subtree_equal

    def __hash__(self) -> int:
        return hash((self.etype, self.rtype, tuple(self.children)))
