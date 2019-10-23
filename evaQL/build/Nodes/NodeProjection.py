from .Node import Node

class NodeProjection(Node):
    def __init__(self, children,attributes=[]):
        self.children = children
        self.attributes = attributes

    def processing(self):
        datainput=self.children.processing()
        data=[]
        for i in range(len(datainput)):
            Tuple=[]
            for e in self.attributes:
                Tuple.append(datainput[i][e])
            data.append(Tuple)
        return data
