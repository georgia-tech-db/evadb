from .Expression import Expression


class ExpressionTuple(Expression):
    def __init__(self,attribute):
        self.attribute = attribute
        self.dictionary={'CLASS':1,'REDNESS':2}
    def evaluate(self,Tuple):
        return Tuple
    def value(self,line):
        return line[self.dictionary[self.attribute]]
