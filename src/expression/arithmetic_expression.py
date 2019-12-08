from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType, ExpressionReturnType
from src.models.storage.batch import FrameBatch


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

    def evaluate(self, batch:FrameBatch):
        frames = [frame._data for frame in batch._frames]
        vl = self.get_child(0).evaluate(frames)
        vr = self.get_child(1).evaluate(frames)

        if (self.etype == ExpressionType.ARITHMETIC_ADD):
            return vl + vr
        elif(self.etype == ExpressionType.ARITHMETIC_SUBTRACT):
            return vl - vr
        elif(self.etype == ExpressionType.ARITHMETIC_MULTIPLY):
            return vl * vr
        elif(self.etype == ExpressionType.ARITHMETIC_DIVIDE):
            return vl / vr

