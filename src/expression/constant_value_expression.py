from .abstract_expression import AbstractExpression, ExpressionType


class ConstantValueExpression(AbstractExpression):
    # ToDo Implement generic value class
    # for now we don't assign any class to value
    # it can have types like string, int etc
    # return type not set, handle that based on value
    def __init__(self, value):
        super().__init__(ExpressionType.CONSTANT_VALUE)
        self._value = value

    def evaluate(self, *args):
        return self._value

    # ToDo implement other functinalities like maintaining hash
    # comparing two objects of this class(==)
