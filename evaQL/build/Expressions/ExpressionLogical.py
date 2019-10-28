from .Expression import Expression

class ExpressionLogical(Expression):
    def __init__(self, children,operator):
        self.operator = operator
        self.children = children
    
    def evaluate(self,Tuple):
        datainput=[]
        for i in range(len(self.children)):
            datainput.append(self.children[i].evaluate(Tuple))
        if self.operator=='AND':
            output=True
            for i in range(len(datainput)):
                output=output and datainput[i]
        if self.operator=='OR':
            output=False
            for i in range(len(datainput)):
                output=output or datainput[i]
        return output
