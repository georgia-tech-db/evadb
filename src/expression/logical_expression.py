import operator

from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType
from src.expression.comparison_expression import ComparisonExpression


class LogicalExpression(AbstractExpression):
    def __init__(self, left_expression, operator, right_expression):
        self.operator = operator
        self.left_expression = left_expression
        self.right_expression = right_expression

    def evaluate(self, tup=[]):
        if isinstance(self.left_expression, LogicalExpression):
            left_exp = self.left_expression.evaluate()
        elif isinstance(self.left_expression, ComparisonExpression):
            left_exp = self.left_expression.evaluate(tup, None)
        else:
            if isinstance(self.left_expression, list):
                left_exp = self.left_expression[0].evaluate()
                for element in self.left_expression[1:]:
                    if self.operator == ExpressionType.LOGICAL_AND:
                        left_exp = left_exp and element.evaluate()
                    elif self.operator == ExpressionType.LOGICAL_OR:
                        left_exp = left_exp or element.evaluate()
                    else:
                        raise ValueError(
                            "Un-Supported operator passed: " + self.operator)
            else:
                if self.left_expression is None:
                    left_exp = None
                else:
                    left_exp = self.left_expression.evaluate()

        if isinstance(self.right_expression, LogicalExpression):
            right_exp = self.right_expression.evaluate()
        elif isinstance(self.right_expression, ComparisonExpression):
            right_exp = self.right_expression.evaluate(tup, None)
        else:
            if isinstance(self.right_expression, list):
                right_exp = self.right_expression[0].evaluate()
                for element in self.right_expression[1:]:
                    if self.operator == ExpressionType.LOGICAL_AND:
                        right_exp = right_exp and element.evaluate()
                    elif self.operator == ExpressionType.LOGICAL_OR:
                        right_exp = right_exp or element.evaluate()
                    else:
                        raise ValueError(
                            "Un-Supported operator passed: " + self.operator)
            else:
                if self.right_expression is None:
                    right_exp = None
                else:
                    right_exp = self.right_expression.evaluate()

        if self.operator == ExpressionType.LOGICAL_AND:
            return left_exp and right_exp
        elif self.operator == ExpressionType.LOGICAL_OR:
            return left_exp or right_exp
        elif self.operator == ExpressionType.LOGICAL_NOT:
            if left_exp is None:
                return list(map(operator.not_, right_exp))
            elif right_exp is None:
                return list(map(operator.not_, left_exp))
            else:
                raise ValueError(
                    "Either of left or right expression should be None")
        else:
            raise ValueError("Un-Supported operator passed: " + self.operator)

    def getLeftExpression(self, defaultExpression=None):
        if self.left_expression is None:
            return defaultExpression
        else:
            return self.left_expression

    def getRightExpression(self, defaultExpression=None):
        if self.right_expression is None:
            return defaultExpression
        else:
            return self.right_expression

    def getOperator(self):
        return self.operator

    def __eq__(self, other):
        if self.operator == other.operator and \
                self.left_expression == other.left_expression and \
                self.right_expression == other.right_expression:
            return True
        else:
            return False

    def __str__(self):
        if self.operator is not None:
            if self.operator == ExpressionType.LOGICAL_AND:
                operator = " AND "
            elif self.operator == ExpressionType.LOGICAL_OR:
                operator = " OR "
            else:
                operator = " " + self.operator + " "
            return str(self.left_expression) + operator + str(self.right_expression)
