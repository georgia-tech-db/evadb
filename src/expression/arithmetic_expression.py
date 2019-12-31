from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType, ExpressionReturnType


class ArithmeticExpression(AbstractExpression):

    def __init__(self, exp_type: ExpressionType, left: AbstractExpression,
                 right: AbstractExpression):
        children = []
        if left is not None:
            children.append(left)
        if right is not None:
            children.append(right)
        super().__init__(exp_type, rtype=ExpressionReturnType.FLOAT,
                         children=children)

    def evaluate(self, *args):
        vl = self.get_child(0).evaluate(*args)
        vr = self.get_child(1).evaluate(*args)

        if (self.etype == ExpressionType.ARITHMETIC_ADD):
            return vl + vr
        elif(self.etype == ExpressionType.ARITHMETIC_SUBTRACT):
            return vl - vr
        elif(self.etype == ExpressionType.ARITHMETIC_MULTIPLY):
            return vl * vr
        elif(self.etype == ExpressionType.ARITHMETIC_DIVIDE):
            return vl / vr
