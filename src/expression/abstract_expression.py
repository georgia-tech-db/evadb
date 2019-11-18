from abc import ABC, abstractmethod
from enum import IntEnum, unique

from src.utils import generic_utils


@unique
class ExpressionType(IntEnum):
    INVALID = 0,
    COMPARE_EQUAL = 1,
    CONSTANT_VALUE = 2,
    TUPLE_VALUE = 3,
    COMPARE_NOT_EQUAL = 4,
    GREATER = 5,
    LESS = 6,
    GREATER_EQUAL = 7,
    LESS_EQUAL = 8
    # add other types


@unique
class ExpressionReturnType(IntEnum):
    INVALID = 0,
    BOOLEAN = 1,
    INTEGER = 2,
    VARCHAR = 3,
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

    def __eq__(self, other):
        if self._etype == other._etype and self._rtype == other._rtype and self._children == other._children and self._predicates == other._predicates:
            return True
        else:
            return False

    def get_child(self, index: int):
        if index < 0 or index >= len(self._children):
            return None
        else:
            self._children[index]

    def append_child(self, index: int, child):
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
