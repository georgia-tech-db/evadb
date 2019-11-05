from abc import ABC, abstractmethod
from typing import List

from src.planner.types import NodeType


class AbstractPlan:
    '''
    Used for Creating an Abstract Plan,
    every node is of type Abstract Plan,
    nodes can be eg: SelectionNodeType or
    ProjectionNodeType etc.
    '''
    def __init__(self, node_type: NodeType):
        self._node_type = node_type
        self._child_nodes = []

    @property
    def node_type(self):
        return self._node_type

    def append_child(self, child_node:'AbstractPlan'):
        if child_node != None:
            self._child_nodes.append(child_node)

    @property
    def children(self)->List['AbstractPlan']:
        return self._child_nodes[:]

 


