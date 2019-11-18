from src.expression.comparison_expression import ComparisonExpression
from .abstract_expression import AbstractExpression


class LogicalExpression(AbstractExpression):
    def __init__(self, left_expression, operator, right_expression):
        self.operator = operator
        self.left_expression = left_expression
        self.right_expression = right_expression

    def evaluate(self):
        if isinstance(self.left_expression, LogicalExpression):
            left_exp = self.left_expression.evaluate()
        elif isinstance(self.left_expression, ComparisonExpression):
            left_exp = self.left_expression.evaluate([], None)
        else:
            if isinstance(self.left_expression, list):
                left_exp = self.left_expression[0].evaluate()
                for element in self.left_expression[1:]:
                    if self.operator == 'AND':
                        left_exp = left_exp and element.evaluate()
                    elif self.operator == 'OR':
                        left_exp = left_exp or element.evaluate()
                    else:
                        raise ValueError("Un-Supported operator passed: " + self.operator)
            else:
                left_exp = self.left_expression.evaluate()

        if isinstance(self.right_expression, LogicalExpression):
            right_exp = self.right_expression.evaluate()
        elif isinstance(self.right_expression, ComparisonExpression):
            right_exp = self.right_expression.evaluate([], None)
        else:
            if isinstance(self.right_expression, list):
                right_exp = self.right_expression[0].evaluate()
                for element in self.right_expression[1:]:
                    if self.operator == 'AND':
                        right_exp = right_exp and element.evaluate()
                    elif self.operator == 'OR':
                        right_exp = right_exp or element.evaluate()
                    else:
                        raise ValueError("Un-Supported operator passed: " + self.operator)
            else:
                right_exp = self.right_expression.evaluate()

        if self.operator == 'AND':
            return left_exp and right_exp
        elif self.operator == 'OR':
            return left_exp or right_exp
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
        if self.operator == other.operator and self.left_expression == other.left_expression and self.right_expression == other.right_expression:
            return True
        else:
            return False
