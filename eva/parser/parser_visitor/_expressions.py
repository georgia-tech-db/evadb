# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import ast

import numpy as np

from eva.catalog.column_type import ColumnType, DistanceMetric
from eva.expression.abstract_expression import ExpressionType
from eva.expression.comparison_expression import ComparisonExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.logical_expression import LogicalExpression
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.like_expression import LikeExpression
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor

from eva.utils.logging_manager import logger


##################################################################
# EXPRESSIONS
##################################################################
class Expressions(evaql_parserVisitor):
    def visitStringLiteral(self, ctx: evaql_parser.StringLiteralContext):
        # Fix a bug here; 'VAN' Literal gets converted to "'VAN'";
        # Multiple quotes should be removed

        if ctx.STRING_LITERAL() is not None:
            return ConstantValueExpression(ctx.getText()[1:-1], ColumnType.TEXT)
        # todo handle other types
        return self.visitChildren(ctx)

    def visitArrayLiteral(self, ctx: evaql_parser.ArrayLiteralContext):
        res = ConstantValueExpression(
            np.array(ast.literal_eval(ctx.getText())), ColumnType.NDARRAY
        )
        return res

    def visitConstant(self, ctx: evaql_parser.ConstantContext):
        if ctx.REAL_LITERAL() is not None:
            return ConstantValueExpression(float(ctx.getText()), ColumnType.FLOAT)

        if ctx.decimalLiteral() is not None:
            return ConstantValueExpression(
                self.visit(ctx.decimalLiteral()), ColumnType.INTEGER
            )
        return self.visitChildren(ctx)

    def visitLogicalExpression(self, ctx: evaql_parser.LogicalExpressionContext):
        if len(ctx.children) < 3:
            # error scenario, should have 3 children
            return None
        left = self.visit(ctx.getChild(0))
        op = self.visit(ctx.getChild(1))
        right = self.visit(ctx.getChild(2))
        return LogicalExpression(op, left, right)

    def visitBinaryComparisonPredicate(
        self, ctx: evaql_parser.BinaryComparisonPredicateContext
    ):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = self.visit(ctx.comparisonOperator())
        return ComparisonExpression(op, left, right)

    # call stack:
    # visitLikePredicate <- visitPredicateExpression <- visitFromClause <- visitQuerySpecification
    def visitLikePredicate(self, ctx: evaql_parser.LikePredicateContext):
        column = self.visit(ctx.predicate(0))
        src_img_path = self.visit(ctx.predicate(1))

        extractor_func = None

        if column is None:
            raise RuntimeError("No valid column name is provided in the LIKE clause")
        
        if isinstance(column, FunctionExpression):
            extractor_func = column
        elif isinstance(column, TupleValueExpression):
            extractor_func = FunctionExpression(None, "FeatureExtractor")
            extractor_func.append_child(TupleValueExpression(col_name=column.col_name))
        else:
            raise RuntimeError("No valid column name is provided in the LIKE clause")

        
        if src_img_path is not None \
            and isinstance(src_img_path, ConstantValueExpression) \
            and src_img_path.v_type == ColumnType.TEXT:
            pass
        else:
            raise RuntimeError("No valid source image path is provided in the LIKE clause")

        flip: bool = ctx.NOT() is not None

        metric = DistanceMetric.L2
        if ctx.uid() is not None:
            metric_text = ctx.uid().getText()
            if metric_text == "L2":
                metric = DistanceMetric.L2
            if metric_text == "L1":
                metric = DistanceMetric.L1
            if metric_text == "InnerProduct":
                metric = DistanceMetric.InnerProduct

        return LikeExpression(extractor_func, src_img_path, flip, metric)

    def visitNestedExpressionAtom(self, ctx: evaql_parser.NestedExpressionAtomContext):
        # ToDo Can there be >1 expression in this case
        expr = ctx.expression(0)
        return self.visit(expr)

    def visitComparisonOperator(self, ctx: evaql_parser.ComparisonOperatorContext):
        op = ctx.getText()
        if op == "=":
            return ExpressionType.COMPARE_EQUAL
        elif op == "<":
            return ExpressionType.COMPARE_LESSER
        elif op == ">":
            return ExpressionType.COMPARE_GREATER
        elif op == ">=":
            return ExpressionType.COMPARE_GEQ
        elif op == "<=":
            return ExpressionType.COMPARE_LEQ
        elif op == "!=":
            return ExpressionType.COMPARE_NEQ
        elif op == "@>":
            return ExpressionType.COMPARE_CONTAINS
        elif op == "<@":
            return ExpressionType.COMPARE_IS_CONTAINED
        else:
            return ExpressionType.INVALID

    def visitLogicalOperator(self, ctx: evaql_parser.LogicalOperatorContext):
        op = ctx.getText()

        if op.lower() == "or":
            return ExpressionType.LOGICAL_OR
        elif op.lower() == "and":
            return ExpressionType.LOGICAL_AND
        else:
            logger.warning("Find invalid logical operator when parsing.")
            return ExpressionType.INVALID

    def visitExpressionsWithDefaults(
        self, ctx: evaql_parser.ExpressionsWithDefaultsContext
    ):
        expr_list = []
        expressions_with_defaults_count = len(ctx.expressionOrDefault())
        for i in range(expressions_with_defaults_count):
            expression = self.visit(ctx.expressionOrDefault(i))
            expr_list.append(expression)

        return expr_list

    def visitSampleClause(self, ctx: evaql_parser.SampleClauseContext):
        return ConstantValueExpression(self.visitChildren(ctx))
