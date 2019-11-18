from .abstract_expression import AbstractExpression, ExpressionType, \
    ExpressionReturnType


class LogicalExpression(AbstractExpression):
    def __init__(self, exp_type: ExpressionType, left: AbstractExpression,
                 right: AbstractExpression):
        children = []
        if left is not None:
            children.append(left)
        if right is not None:
            children.append(right)
        super().__init__(exp_type, rtype=ExpressionReturnType.BOOLEAN,
                         children=children)

    def evaluate(self, *args):
        
        if len(self._children) == 2 :
            vl = self._children[0].evaluate(*args)
            vr = self._children[1].evaluate(*args)
        else:
            vr = self._children[0].evaluate(*args)


        if (self.etype == ExpressionType.LOGICAL_AND):
            return vl and vr
        elif(self.etype == ExpressionType.LOGICAL_OR):
            return vl or vr
        elif(self.etype == ExpressionType.LOGICAL_NOT):
            return (not vr)
             
