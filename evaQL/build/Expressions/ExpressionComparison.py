from .Expression import Expression
from .ExpressionConstant import ExpressionConstant
from .ExpressionTuple import ExpressionTuple

class ExpressionComparison(Expression):
    def __init__(self,children,operator):
        self.operator = operator
        self.children=children

    def evaluate(self,Tuple):
        dataleft=self.children[0].evaluate(Tuple)
        dataright=self.children[1].evaluate(Tuple)
        if self.operator=='=':
            if self.children[0].value(dataleft)==self.children[1].value(dataright):
                return True
            else:
                return False
        if self.operator=='>':
            if self.children[0].value(dataleft)>self.children[1].value(dataright):
                return True
            else:
                return False
        if self.operator=='<':
            if self.children[0].value(dataleft)<self.children[1].value(dataright):
                return True
            else:
                return False
        if self.operator=='!=':
            if self.children[0].value(dataleft)!=self.children[1].value(dataright):
                return True
            else:
                return False
        if self.operator=='<=':
            if self.children[0].value(dataleft)<=self.children[1].value(dataright):
                return True
            else:
                return False
        if self.operator=='>=':
            if self.children[0].value(dataleft)>=self.children[1].value(dataright):
                return True
            else:
                return False
        
