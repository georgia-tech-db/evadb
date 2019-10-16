from abc import ABC, abstractmethod
from typing import List

class AbstractExecutor(ABC):
    """
    An abstract class for the executor engine
    Arguments:
        node (AbstractPlan): Plan node corresponding to this executor
    """
    def __init__(self, node : AbstractPlan):
        self._node = node
        self._children = []
        self._output = None

    
    def append_child(self, child: AbstractExecutor):
        """
        appends a child exector node 
        
        Arguments:
            child {AbstractExecutor} -- child node
        """
        self._children.append(child)

    @property
    def children(self) -> List[AbstractExecutor]:
        """
        Returns the list of child executor
        Returns:
            [] -- list of children
        """
        return self._children
    
    @property
    def output(self) -> FrameBatch:
        return self._output

    @output.setter
    def output(self, output : FrameBatch):
        self._output = output
    
    
    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def execute(self):
        pass

