from .Node import Node

class NodeProjection(Node):
    def __init__(self, children,attributes=[]):
        self.children = children
        self.attributes = attributes

