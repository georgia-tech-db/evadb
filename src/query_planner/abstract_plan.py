from abc import ABC, abstractmethod
from enum import IntEnum, unique


@unique
class PlanNodeType(IntEnum):
    SEQSCAN = 1
    # add other types
    LOGICAL_SELECT = 2,
    LOGICAL_PROJECTION = 3
    LOGICAL_INNER_JOIN = 4
    TABLE = 5


class AbstractPlan(ABC):

    def __init__(self):
        self._children = []
        self._parent = None
        # self._node_type = node_type

    def append_child(self, child):
        """append node to children list
        
        Arguments:
            child {AbstractPlan} -- input child node
        """
        self._children.append(child)

    def set_children(self, children):
        """create new child list for node

        Arguments:
            children list of {AbstractPlan} nodes
        """
        self._children = children

    @property
    def parent(self):
        """Returns the parent of current node
        
        Returns:
            AbstractPlan -- parent node
        """
        return self._parent

    @parent.setter
    def parent(self, node: 'AbstractPlan'):
        """returns parent of current node
        
        Arguments:
            node {AbstractPlan} -- parent node
        """
        # remove if we don't allow setter function
        # parent can be constructor only job
        self._parent = node

    @property
    def children(self):
        """returns children list pf current node
        
        Returns:
            List[AbstractPlan] -- children list
        """
        return self._children

    @abstractmethod
    def get_node_type(self) -> PlanNodeType:
        pass

    def __str__(self, level=0):
        out_string = "\t" * level + '' + "\n"
        for child in self.children:
            out_string += child.__str__(level + 1)
        return out_string