
from src.expression.abstract_expression import (AbstractExpression,
                                                ExpressionType)
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.logical_expression import LogicalExpression


from src.parser.evaql.evaql_parser import evaql_parser


##################################################################
# EXPRESSIONS
##################################################################

def visitStringLiteral(self, ctx: evaql_parser.StringLiteralContext):
    # Fix a bug here; 'VAN' Literal gets converted to "'VAN'";
    # Multiple quotes should be removed

    if ctx.STRING_LITERAL() is not None:
        return ConstantValueExpression(ctx.getText()[1:-1])
    # todo handle other types
    return self.visitChildren(ctx)


def visitConstant(self, ctx: evaql_parser.ConstantContext):
    if ctx.REAL_LITERAL() is not None:
        return ConstantValueExpression(float(ctx.getText()))

    if ctx.decimalLiteral() is not None:
        return ConstantValueExpression(self.visit(ctx.decimalLiteral()))
    return self.visitChildren(ctx)


def visitLogicalExpression(
        self, ctx: evaql_parser.LogicalExpressionContext):
    if len(ctx.children) < 3:
        # error scenario, should have 3 children
        return None
    left = self.visit(ctx.getChild(0))
    op = self.visit(ctx.getChild(1))
    right = self.visit(ctx.getChild(2))
    return LogicalExpression(op, left, right)


def visitBinaryComparisonPredicate(
        self, ctx: evaql_parser.BinaryComparisonPredicateContext):
    left = self.visit(ctx.left)
    right = self.visit(ctx.right)
    op = self.visit(ctx.comparisonOperator())
    return ComparisonExpression(op, left, right)


def visitNestedExpressionAtom(
        self, ctx: evaql_parser.NestedExpressionAtomContext):
    # ToDo Can there be >1 expression in this case
    expr = ctx.expression(0)
    return self.visit(expr)


def visitComparisonOperator(
        self, ctx: evaql_parser.ComparisonOperatorContext):
    op = ctx.getText()
    if op == '=':
        return ExpressionType.COMPARE_EQUAL
    elif op == '<':
        return ExpressionType.COMPARE_LESSER
    elif op == '>':
        return ExpressionType.COMPARE_GREATER
    else:
        return ExpressionType.INVALID


def visitLogicalOperator(self, ctx: evaql_parser.LogicalOperatorContext):
    op = ctx.getText()

    if op == 'OR':
        return ExpressionType.LOGICAL_OR
    elif op == 'AND':
        return ExpressionType.LOGICAL_AND
    else:
        return ExpressionType.INVALID


def visitExpressionsWithDefaults(
        self, ctx: evaql_parser.ExpressionsWithDefaultsContext):
    expr_list = []
    expressions_with_defaults_count = len(ctx.expressionOrDefault())
    for i in range(expressions_with_defaults_count):
        expression = self.visit(ctx.expressionOrDefault(i))
        expr_list.append(expression)

    return expr_list
