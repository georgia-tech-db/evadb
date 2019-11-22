from abc import ABC, abstractmethod
from typing import List, Iterator

from src.models.storage.batch import FrameBatch
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
    def next(self) -> Iterator[FrameBatch]:
        """
        This method is implemented by every executor. Includes logic for
        fetching frame batches from child nodes and emitting it to parent
        node.

        Yields:
             FrameBatch
        """
        NotImplementedError('Must be implemented in subclasses.')
