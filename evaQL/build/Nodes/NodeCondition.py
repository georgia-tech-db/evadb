from .Node import Node

class NodeCondition(Node):
    def __init__(self, children,expression):
        self.children = children
        self.expression = expression

    def processing(self):
        datainput=self.children.processing()
        data=[]
        for i in range(len(datainput)):
            if self.expression.evaluate(datainput[i]):
                data.append(datainput[i])
        return data
