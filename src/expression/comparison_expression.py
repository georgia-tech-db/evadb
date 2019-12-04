from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType, \
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
        left_values = self.get_child(0).evaluate(*args)
        right_values = self.get_child(1).evaluate(*args)

        # Broadcasting scalars
        if type(right_values) is not list:
            right_values = [right_values] * len(left_values)
        # TODO implement a better way to compare value_left and value_right
        # Implement a generic return type
        outcome = []
        for value_left, value_right in zip(left_values, right_values):
            if self.etype == ExpressionType.COMPARE_EQUAL:
                outcome.append(value_left == value_right)
            elif self.etype == ExpressionType.COMPARE_GREATER:
                outcome.append(value_left > value_right)
            elif self.etype == ExpressionType.COMPARE_LESSER:
                outcome.append(value_left < value_right)
            elif self.etype == ExpressionType.COMPARE_GEQ:
                outcome.append(value_left >= value_right)
            elif self.etype == ExpressionType.COMPARE_LEQ:
                outcome.append(value_left <= value_right)
            elif self.etype == ExpressionType.COMPARE_NEQ:
                outcome.append(value_left != value_right)
            else:
                raise ValueError("Not supported types.")

        return outcome
        # ToDo add other comparision types

    def getLeft(self):
        return self._children[0]

    def getRight(self):
        return self._children[1]

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