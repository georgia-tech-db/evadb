from .Expression import Expression

class ExpressionArithmetic(Expression):
    def __init__(self,children,operator):
        self.operator = operator
        self.children=children

    def evaluate(self,Tuple):
        return Tuple
    def value(self,line):
        if self.operator=='+':
            return self.children[0].value(line)+self.children[1].value(line)
        if self.operator=='-':
            return self.children[0].value(line)-self.children[1].value(line)
        if self.operator=='*':
            return self.children[0].value(line)*self.children[1].value(line)
        if self.operator=='/':
            return self.children[0].value(line)/self.children[1].value(line)
