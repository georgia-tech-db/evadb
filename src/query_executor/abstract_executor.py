from abc import ABC, abstractmethod
from typing import List

from src.models import FrameBatch
from src.query_planner.abstract_plan import AbstractPlan


class AbstractExecutor(ABC):
    """
    An abstract class for the executor engine
    Arguments:
        node (AbstractPlan): Plan node corresponding to this executor
    """

    def __init__(self, node: 'AbstractPlan'):
        self._node = node
        self._children = []

    def append_child(self, child: 'AbstractExecutor'):
        """
        appends a child exector node 
        
        Arguments:
            child {AbstractExecutor} -- child node
        """
        self._children.append(child)

    @property
    def children(self) -> List['AbstractExecutor']:
        """
        Returns the list of child executor
        Returns:
            [] -- list of children
        """
        return self._children

    @abstractmethod
    def validate(self):
        NotImplementedError('Must be implemented in subclasses.')

    @abstractmethod
    def execute(self, batch: FrameBatch):
        NotImplementedError('Must be implemented in subclasses.')
