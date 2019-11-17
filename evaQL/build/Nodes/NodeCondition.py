from .Node import Node

class NodeCondition(Node):
    def __init__(self, children,expression):
        self.children = children
        self.expression = expression


