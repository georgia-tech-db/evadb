from src.expression.abstract_expression import AbstractExpression, ExpressionType, \
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
        vl = self.get_child(0).evaluate(*args)
        vr = self.get_child(1).evaluate(*args)

        if (self.etype == ExpressionType.COMPARE_EQUAL):
            return vl == vr
        elif(self.etype == ExpressionType.COMPARE_GREATER):
            return vl > vr
        elif(self.etype == ExpressionType.COMPARE_LESSER):
            return vl < vr
        elif(self.etype == ExpressionType.COMPARE_GEQ):
            return vl >= vr
        elif(self.etype == ExpressionType.COMPARE_LEQ):
            return vl <= vr
        elif(self.etype == ExpressionType.COMPARE_NEQ):
            return vl != vr          
