from .abstract_expression import AbstractExpression, ExpressionType


class ArithmeticExpression(AbstractExpression):

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
        vl = self._children[0].evaluate(*args)
        vr = self._children[1].evaluate(*args)

        # ToDo implement a better way to compare vl and vr
        # Implement a generic return type

        if (self.etype == ExpressionType.ADDITION):
            return vl + vr
        elif(self.etype == ExpressionType.SUBTRACTION):
            return vl - vr
        elif(self.etype == ExpressionType.MULTIPLICATION):
            return vl * vr
        elif(self.etype == ExpressionType.DIVISION):
            return vl / vr

