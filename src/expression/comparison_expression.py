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
        vls = self.get_child(0).evaluate(*args)
        vrs = self.get_child(1).evaluate(*args)

        # Broadcasting scalars
        if type(vrs) is not list:
            vrs = [vrs] * len(vls)
        # TODO implement a better way to compare vl and vr
        # Implement a generic return type
        outcome = []
        for vl, vr in zip(vls, vrs):
            if self.etype == ExpressionType.COMPARE_EQUAL:
                outcome.append(vl.eq(vr))
        return outcome

        # ToDo add other comparision types
