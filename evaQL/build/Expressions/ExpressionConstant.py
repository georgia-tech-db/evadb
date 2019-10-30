from .Expression import Expression

class ExpressionConstant(Expression):
    def __init__(self,data):
        self.data=data
    def evaluate(self,Tuple):
        return self.data
    def value(self,line):
        if self.data.isnumeric():
            return float(self.data)
        else:
            return self.data
