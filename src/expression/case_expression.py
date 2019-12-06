from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType, \
    ExpressionReturnType


class CaseExpression(AbstractExpression):
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
        conditions = self.get_child(0).evaluate(*args)
        
        outcome = []

        for case in range(self.get_children_count()):
            left_values = self.get_child(0).evaluate(*args)
            if(case == (self.get_children_count() - 1)):
                outcome.append(left_values)
            right_values = self.get_child(1).evaluate(*args)

            if (left_values == True):
                outcome.append(right_values)
                break        

        return outcome
