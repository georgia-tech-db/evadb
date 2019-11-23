from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType, \
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
        if self.get_children_count() == 2:
            outcomes = []
            left_values = self.get_child(0).evaluate(*args)
            right_values = self.get_child(1).evaluate(*args)
            for value_left, value_right in zip(left_values, right_values):
                if self.etype == ExpressionType.LOGICAL_AND:
                    outcomes.append(value_left and value_right)
                elif self.etype == ExpressionType.LOGICAL_OR:
                    outcomes.append(value_left or value_right)
            return outcomes

        else:
            values = self.get_child(0).evaluate(*args)

            if self.etype == ExpressionType.LOGICAL_NOT:
                return [not value for value in values]
