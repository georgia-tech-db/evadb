from .abstract_expression import AbstractExpression, ExpressionType, \
    ExpressionReturnType


class ComparisonExpression(AbstractExpression):
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
        if (self.etype == ExpressionType.COMPARE_EQUAL):
            return vl == vr
        # ToDo add other comparision types

    def __str__(self):
        op = None
        if self.etype == ExpressionType.COMPARE_EQUAL:
            op = '='
        elif self.etype == ExpressionType.COMPARE_NOT_EQUAL:
            op = '!='
        else:
            raise Exception('Operator is not supported')
        vl = self._children[0].evaluate()
        vr = self._children[1].evaluate()
        return str(vl) + str(op) + str(vr)


