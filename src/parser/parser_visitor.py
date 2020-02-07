# coding=utf-8
# Copyright 2018-2020 EVA
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

import warnings

from antlr4 import TerminalNode

from src.expression.abstract_expression import (AbstractExpression,
                                                ExpressionType)
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.logical_expression import LogicalExpression
from src.expression.tuple_value_expression import TupleValueExpression

from src.parser.select_statement import SelectStatement
from src.parser.create_statement import CreateTableStatement
from src.parser.insert_statement import InsertTableStatement

from src.parser.table_ref import TableRef, TableInfo

from src.parser.evaql.evaql_parser import evaql_parser
from src.parser.evaql.evaql_parserVisitor import evaql_parserVisitor

from src.catalog.column_type import ColumnType
from src.catalog.df_column import DataframeColumn


class ParserVisitor(evaql_parserVisitor):

    def visitRoot(self, ctx: evaql_parser.RootContext):
        for child in ctx.children:
            if child is not TerminalNode:
                return self.visit(child)

    def visitSqlStatements(self, ctx: evaql_parser.SqlStatementsContext):
        eva_statements = []
        for child in ctx.children:
            stmt = self.visit(child)
            if stmt is not None:
                eva_statements.append(stmt)

        return eva_statements

    ##################################################################
    # STATEMENTS
    ##################################################################

    def visitDdlStatement(self, ctx: evaql_parser.DdlStatementContext):
        ddl_statement = self.visitChildren(ctx)
        return ddl_statement

    def visitDmlStatement(self, ctx: evaql_parser.DdlStatementContext):
        dml_statement = self.visitChildren(ctx)
        return dml_statement

    ##################################################################
    # INSERT STATEMENTS
    ##################################################################

    def visitInsertStatement(self, ctx: evaql_parser.InsertStatementContext):
        table_ref = None
        column_list = []
        value_list = []
        # first two children with be INSERT INTO
        # Then we will have terminal nodes for '(', ')'
        for child in ctx.children[2:]:
            if not isinstance(child, TerminalNode):
                try:
                    rule_idx = child.getRuleIndex()

                    if rule_idx == evaql_parser.RULE_tableName:
                        table_ref = self.visit(ctx.tableName())

                    elif rule_idx == evaql_parser.RULE_uidList:
                        column_list = self.visit(ctx.uidList())

                    elif rule_idx == evaql_parser.RULE_insertStatementValue:
                        insrt_value = self.visit(ctx.insertStatementValue())
                        # Support only (value1, value2, .... value n)
                        value_list = insrt_value[0]
                except BaseException:
                    print("Exception")
                    # stop parsing something bad happened
                    return None

        insert_stmt = InsertTableStatement(table_ref, column_list, value_list)
        return insert_stmt

    def visitUidList(self, ctx: evaql_parser.UidListContext):
        uid_list = []
        for child in ctx.children:
            # Skippping commas
            if not isinstance(child, TerminalNode):
                uid = self.visit(child)
                uid_expr = TupleValueExpression(uid)
                uid_list.append(uid_expr)

        return uid_list

    def visitInsertStatementValue(
            self, ctx: evaql_parser.InsertStatementValueContext):
        insert_stmt_value = []
        for child in ctx.children:
            if not isinstance(child, TerminalNode):
                try:
                    rule_idx = child.getRuleIndex()

                    if rule_idx == evaql_parser.RULE_expressionsWithDefaults:
                        expr = self.visit(child)
                        insert_stmt_value.append(expr)

                except BaseException:
                    print("Exception")
                    # stop parsing something bad happened
                    return None
        return insert_stmt_value

    ##################################################################
    # CREATE STATEMENTS
    ##################################################################

    def visitColumnCreateTable(
            self, ctx: evaql_parser.ColumnCreateTableContext):

        table_ref = None
        if_not_exists = False
        create_definitions = []

        # first two children will be CREATE TABLE terminal token
        for child in ctx.children[2:]:
            try:
                rule_idx = child.getRuleIndex()

                if rule_idx == evaql_parser.RULE_tableName:
                    table_ref = self.visit(ctx.tableName())

                elif rule_idx == evaql_parser.RULE_ifNotExists:
                    if_not_exists = True

                elif rule_idx == evaql_parser.RULE_createDefinitions:
                    create_definitions = self.visit(ctx.createDefinitions())

            except BaseException:
                print("Exception")
                # stop parsing something bad happened
                return None

        create_stmt = CreateTableStatement(table_ref,
                                           if_not_exists,
                                           create_definitions)
        return create_stmt

    def visitCreateDefinitions(
            self, ctx: evaql_parser.CreateDefinitionsContext):
        column_definitions = []
        child_index = 0
        for child in ctx.children:
            create_definition = ctx.createDefinition(child_index)
            if create_definition is not None:
                column_definition = self.visit(create_definition)
                column_definitions.append(column_definition)
            child_index = child_index + 1

        return column_definitions

    def visitColumnDeclaration(
            self, ctx: evaql_parser.ColumnDeclarationContext):

        data_type, dimensions = self.visit(ctx.columnDefinition())
        column_name = self.visit(ctx.uid())

        column = DataframeColumn(column_name, data_type,
                                 array_dimensions=dimensions)
        return column

    def visitColumnDefinition(self, ctx: evaql_parser.ColumnDefinitionContext):

        data_type, dimensions = self.visit(ctx.dataType())
        return data_type, dimensions

    def visitSimpleDataType(self, ctx: evaql_parser.SimpleDataTypeContext):

        data_type = None
        dimensions = []

        if ctx.BOOLEAN() is not None:
            data_type = ColumnType.BOOLEAN

        return data_type, dimensions

    def visitIntegerDataType(self, ctx: evaql_parser.IntegerDataTypeContext):

        data_type = None
        dimensions = []

        if ctx.INTEGER() is not None:
            data_type = ColumnType.INTEGER
        elif ctx.UNSIGNED() is not None:
            data_type = ColumnType.INTEGER

        return data_type, dimensions

    def visitDimensionDataType(
            self, ctx: evaql_parser.DimensionDataTypeContext):
        data_type = None
        dimensions = []

        if ctx.FLOAT() is not None:
            data_type = ColumnType.FLOAT
            dimensions = self.visit(ctx.lengthTwoDimension())
        elif ctx.TEXT() is not None:
            data_type = ColumnType.TEXT
            dimensions = self.visit(ctx.lengthOneDimension())
        elif ctx.NDARRAY() is not None:
            data_type = ColumnType.NDARRAY
            dimensions = self.visit(ctx.lengthDimensionList())

        return data_type, dimensions

    def visitLengthOneDimension(
            self, ctx: evaql_parser.LengthOneDimensionContext):
        dimensions = []

        if ctx.decimalLiteral() is not None:
            dimensions = [self.visit(ctx.decimalLiteral())]

        return dimensions

    def visitLengthTwoDimension(
            self, ctx: evaql_parser.LengthTwoDimensionContext):
        first_decimal = self.visit(ctx.decimalLiteral(0))
        second_decimal = self.visit(ctx.decimalLiteral(1))

        dimensions = [first_decimal, second_decimal]
        return dimensions

    def visitLengthDimensionList(
            self, ctx: evaql_parser.LengthDimensionListContext):
        dimensions = []
        dimension_index = 0
        for child in ctx.children:
            decimal_literal = ctx.decimalLiteral(dimension_index)
            if decimal_literal is not None:
                decimal = self.visit(decimal_literal)
                dimensions.append(decimal)
            dimension_index = dimension_index + 1

        return dimensions

    def visitDecimalLiteral(self, ctx: evaql_parser.DecimalLiteralContext):

        decimal = None
        if ctx.DECIMAL_LITERAL() is not None:
            decimal = int(str(ctx.DECIMAL_LITERAL()))
        elif ctx.ONE_DECIMAL() is not None:
            decimal = int(str(ctx.ONE_DECIMAL()))
        elif ctx.TWO_DECIMAL() is not None:
            decimal = int(str(ctx.TWO_DECIMAL()))
        elif ctx.ZERO_DECIMAL() is not None:
            decimal = int(str(ctx.ZERO_DECIMAL()))

        return decimal

    ##################################################################
    # SELECT STATEMENT
    ##################################################################

    def visitSimpleSelect(self, ctx: evaql_parser.SimpleSelectContext):
        select_stmt = self.visitChildren(ctx)
        return select_stmt

    ##################################################################
    # TABLE SOURCES
    ##################################################################

    def visitTableSources(self, ctx: evaql_parser.TableSourcesContext):
        table_list = []
        for child in ctx.children:
            table = self.visit(child)
            if table is not None:
                table_list.append(table)
        return table_list

    def visitQuerySpecification(
            self, ctx: evaql_parser.QuerySpecificationContext):
        target_list = None
        from_clause = None
        where_clause = None
        # first child will be a SELECT terminal token
        for child in ctx.children[1:]:
            try:
                rule_idx = child.getRuleIndex()
                if rule_idx == evaql_parser.RULE_selectElements:
                    target_list = self.visit(child)

                elif rule_idx == evaql_parser.RULE_fromClause:
                    clause = self.visit(child)
                    from_clause = clause.get('from', None)
                    where_clause = clause.get('where', None)

            except BaseException:
                # stop parsing something bad happened
                return None

        # we don't support multiple table sources
        if from_clause is not None:
            from_clause = from_clause[0]

        select_stmt = SelectStatement(target_list, from_clause, where_clause)

        return select_stmt

    def visitSelectElements(self, ctx: evaql_parser.SelectElementsContext):
        select_list = []
        for child in ctx.children:
            element = self.visit(child)
            if element is not None:
                select_list.append(element)

        return select_list

    def visitFromClause(self, ctx: evaql_parser.FromClauseContext):
        from_table = None
        where_clause = None

        if ctx.tableSources():
            from_table = self.visit(ctx.tableSources())
        if ctx.whereExpr is not None:
            where_clause = self.visit(ctx.whereExpr)

        return {"from": from_table, "where": where_clause}

    def visitTableName(self, ctx: evaql_parser.TableNameContext):

        table_name = self.visit(ctx.fullId())
        if table_name is not None:
            table_info = TableInfo(table_name=table_name)
            return TableRef(table_info)
        else:
            warnings.warn("Invalid from table", SyntaxWarning)

    def visitFullColumnName(self, ctx: evaql_parser.FullColumnNameContext):
        # dotted id not supported yet
        column_name = self.visit(ctx.uid())
        if column_name is not None:
            return TupleValueExpression(col_name=column_name)
        else:
            warnings.warn("Column Name Missing", SyntaxWarning)

    def visitSimpleId(self, ctx: evaql_parser.SimpleIdContext):
        # todo handle children, right now assuming TupleValueExpr
        return ctx.getText()
        # return self.visitChildren(ctx)

    ##################################################################
    # EXPRESSIONS
    ##################################################################

    def visitStringLiteral(self, ctx: evaql_parser.StringLiteralContext):
        # Fix a bug here; 'VAN' Literal gets converted to "'VAN'";
        # Multiple quotes should be removed

        if ctx.STRING_LITERAL() is not None:
            return ConstantValueExpression(ctx.getText())
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

    def visitBinaryComparasionPredicate(
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
        for child in ctx.children:
            # ignore COMMAs
            if not isinstance(child, TerminalNode):
                expr = self.visit(child)
                expr_list.append(expr)

        return expr_list
