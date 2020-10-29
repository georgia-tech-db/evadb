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

from src.expression.abstract_expression import (ExpressionType)
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.function_expression import FunctionExpression, \
    ExecutionMode
from src.expression.logical_expression import LogicalExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.parser.create_statement import CreateTableStatement, ColumnDefinition
from src.parser.create_udf_statement import CreateUDFStatement
from src.parser.evaql.evaql_parser import evaql_parser
from src.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from src.parser.insert_statement import InsertTableStatement
from src.parser.select_statement import SelectStatement
from src.parser.table_ref import TableRef, TableInfo
from src.parser.types import ParserColumnDataType
from src.parser.load_statement import LoadDataStatement
from src.parser.create_mat_view_statement \
    import CreateMaterializedViewStatement

from src.parser.types import ColumnConstraintEnum
from src.parser.create_statement import ColConstraintInfo

from src.utils.logging_manager import LoggingLevel, LoggingManager


class ParserVisitor(evaql_parserVisitor):

    def visitRoot(self, ctx: evaql_parser.RootContext):
        for child in ctx.children:
            if child is not TerminalNode:
                return self.visit(child)

    def visitSqlStatements(self, ctx: evaql_parser.SqlStatementsContext):
        eva_statements = []
        sql_statement_count = len(ctx.sqlStatement())
        for child_index in range(sql_statement_count):
            statement = self.visit(ctx.sqlStatement(child_index))
            eva_statements.append(statement)
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
        uid_list_length = len(ctx.uid())
        for uid_index in range(uid_list_length):
            uid = self.visit(ctx.uid(uid_index))
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

        data_type, dimensions, column_constraint_information = self.visit(
            ctx.columnDefinition())

        column_name = self.visit(ctx.uid())

        if column_name is not None:
            return ColumnDefinition(
                column_name, data_type, dimensions,
                column_constraint_information)

    def visitColumnDefinition(self, ctx: evaql_parser.ColumnDefinitionContext):

        data_type, dimensions = self.visit(ctx.dataType())

        constraint_count = len(ctx.columnConstraint())

        column_constraint_information = ColConstraintInfo()

        for i in range(constraint_count):
            return_type = self.visit(ctx.columnConstraint(i))
            if return_type == ColumnConstraintEnum.UNIQUE:

                column_constraint_information.unique = True

        return data_type, dimensions, column_constraint_information

    def visitUniqueKeyColumnConstraint(
            self, ctx: evaql_parser.UniqueKeyColumnConstraintContext):
        return ColumnConstraintEnum.UNIQUE

    def visitSimpleDataType(self, ctx: evaql_parser.SimpleDataTypeContext):

        data_type = None
        dimensions = []

        if ctx.BOOLEAN() is not None:
            data_type = ParserColumnDataType.BOOLEAN

        return data_type, dimensions

    def visitIntegerDataType(self, ctx: evaql_parser.IntegerDataTypeContext):

        data_type = None
        dimensions = []

        if ctx.INTEGER() is not None:
            data_type = ParserColumnDataType.INTEGER
        elif ctx.UNSIGNED() is not None:
            data_type = ParserColumnDataType.INTEGER

        return data_type, dimensions

    def visitDimensionDataType(
            self, ctx: evaql_parser.DimensionDataTypeContext):
        data_type = None
        dimensions = []

        if ctx.FLOAT() is not None:
            data_type = ParserColumnDataType.FLOAT
            dimensions = self.visit(ctx.lengthTwoDimension())
        elif ctx.TEXT() is not None:
            data_type = ParserColumnDataType.TEXT
            dimensions = self.visit(ctx.lengthOneDimension())
        elif ctx.NDARRAY() is not None:
            data_type = ParserColumnDataType.NDARRAY
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
        dimension_list_length = len(ctx.decimalLiteral())
        for dimension_list_index in range(dimension_list_length):
            decimal_literal = ctx.decimalLiteral(dimension_list_index)
            decimal = self.visit(decimal_literal)
            dimensions.append(decimal)

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
        table_sources_count = len(ctx.tableSource())
        for table_sources_index in range(table_sources_count):
            table = self.visit(ctx.tableSource(table_sources_index))
            table_list.append(table)

        return table_list

    # Nested sub query
    def visitSubqueryTableItem(
            self, ctx: evaql_parser.SubqueryTableItemContext):
        return self.visit(ctx.selectStatement())

    def visitUnionSelect(self, ctx: evaql_parser.UnionSelectContext):
        left_selectStatement = self.visit(ctx.left)
        right_selectStatement = self.visit(ctx.right)
        # This makes a difference becasue the LL parser (Left-to-right)
        while right_selectStatement.union_link is not None:
            right_selectStatement = right_selectStatement.union_link
        # We need to check the correctness for union operator.
        # Here when parsing or later operator, plan?
        right_selectStatement.union_link = left_selectStatement
        if ctx.unionAll is None:
            right_selectStatement.union_all = False
        else:
            right_selectStatement.union_all = True
        return right_selectStatement

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
        select_elements_count = len(ctx.selectElement())
        for select_element_index in range(select_elements_count):
            element = self.visit(ctx.selectElement(select_element_index))
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

    ##################################################################
    # LOAD STATEMENT
    ##################################################################

    def visitLoadStatement(self, ctx: evaql_parser.LoadStatementContext):
        file_path = self.visit(ctx.fileName()).value
        table = self.visit(ctx.tableName())
        stmt = LoadDataStatement(table, file_path)
        return stmt

    ##################################################################
    # COMMON CLAUSES Ids, Column_names, Table_names
    ##################################################################

    def visitTableName(self, ctx: evaql_parser.TableNameContext):

        table_name = self.visit(ctx.fullId())
        if table_name is not None:
            table_info = TableInfo(table_name=table_name)
            return TableRef(table_info)
        else:
            warnings.warn("Invalid from table", SyntaxWarning)

    def visitFullColumnName(self, ctx: evaql_parser.FullColumnNameContext):
        # Adding support for a.b
        # Will restrict implementation to raise error for a.b.c
        dottedIds = []
        if ctx.dottedId():
            if len(ctx.dottedId()) != 1:
                LoggingManager().log("Only tablename.colname syntax supported",
                                     LoggingLevel.ERROR)
                return
            for id in ctx.dottedId():
                dottedIds.append(self.visit(id))

        uid = self.visit(ctx.uid())

        if len(dottedIds):
            return TupleValueExpression(table_name=uid, col_name=dottedIds[0])
        else:
            return TupleValueExpression(col_name=uid)

    def visitSimpleId(self, ctx: evaql_parser.SimpleIdContext):
        # todo handle children, right now assuming TupleValueExpr
        return ctx.getText()
        # return self.visitChildren(ctx)

    def visitDottedId(self, ctx: evaql_parser.DOT_ID):
        if ctx.DOT_ID():
            return ctx.getText()[1:]
        if ctx.uid():
            return self.visit(ctx.uid())

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
        elif op == '>=':
            return ExpressionType.COMPARE_GEQ
        elif op == '<=':
            return ExpressionType.COMPARE_LEQ
        elif op == '!=':
            return ExpressionType.COMPARE_NEQ
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

    ##################################################################
    # Functions - UDFs, Aggregate Windowed functions
    ##################################################################
    def visitUdfFunction(self, ctx: evaql_parser.UdfFunctionContext):
        udf_name = None
        udf_output = None
        if ctx.simpleId():
            udf_name = self.visit(ctx.simpleId())
        else:
            LoggingManager().log('UDF function name missing.',
                                 LoggingLevel.ERROR)
        if ctx.dottedId():
            udf_output = self.visit(ctx.dottedId())

        udf_args = self.visit(ctx.functionArgs())
        func_expr = FunctionExpression(None, name=udf_name,
                                       mode=ExecutionMode.EXEC,
                                       output=udf_output)
        for arg in udf_args:
            func_expr.append_child(arg)

        return func_expr

    def visitFunctionArgs(self, ctx: evaql_parser.FunctionArgsContext):
        args = []
        for child in ctx.children:
            # ignore COMMAs
            if not isinstance(child, TerminalNode):
                args.append(self.visit(child))
        return args

    # Create UDF
    def visitCreateUdf(self, ctx: evaql_parser.CreateUdfContext):
        udf_name = None
        if_not_exists = False
        input_definitions = []
        output_definitions = []
        impl_path = None
        udf_type = None

        for child in ctx.children:
            try:
                if isinstance(child, TerminalNode):
                    continue
                rule_idx = child.getRuleIndex()

                if rule_idx == evaql_parser.RULE_udfName:
                    udf_name = self.visit(ctx.udfName())

                elif rule_idx == evaql_parser.RULE_ifNotExists:
                    if_not_exists = True

                elif rule_idx == evaql_parser.RULE_createDefinitions:
                    # There should be 2 createDefinition
                    # idx 0 describing udf INPUT
                    # idx 1 describing udf OUTPUT
                    if len(ctx.createDefinitions()) != 2:
                        LoggingManager().log('UDF Input or Output Missing',
                                             LoggingLevel.ERROR)
                    input_definitions = self.visit(ctx.createDefinitions(0))
                    output_definitions = self.visit(ctx.createDefinitions(1))

                elif rule_idx == evaql_parser.RULE_udfType:
                    udf_type = self.visit(ctx.udfType())

                elif rule_idx == evaql_parser.RULE_udfImpl:
                    impl_path = self.visit(ctx.udfImpl()).value

            except BaseException:
                LoggingManager().log('CREATE UDF Failed', LoggingLevel.ERROR)
                # stop parsing something bad happened
                return None
        stmt = CreateUDFStatement(
            udf_name,
            if_not_exists,
            input_definitions,
            output_definitions,
            impl_path,
            udf_type)
        return stmt

    # MATERIALIZED VIEW
    def visitCreateMaterializedView(self, ctx: evaql_parser.CreateMaterializedViewContext):
        view_name = self.visit(ctx.tableName())
        if_not_exists = False
        if ctx.ifNotExists():
            if_not_exists = self.visit(ctx.ifNotExists())
        uid_list = self.visit(ctx.uidList())
        # setting all other column definition attributes as None,
        # need to figure from query outout
        col_list = [ColumnDefinition(
            uid.col_name, None, None) for uid in uid_list]
        query = self.visit(ctx.selectStatement())
        return CreateMaterializedViewStatement(view_name, col_list,
                                               if_not_exists, query)
