
from antlr4 import TerminalNode
from src.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from src.parser.evaql.evaql_parser import evaql_parser
from src.parser.create_udf_statement import CreateUDFStatement
from src.expression.function_expression import FunctionExpression



class ParserVisitor(evaql_parserVisitor):
    from ._insert_statements import visitInsertStatement, visitUidList, visitInsertStatementValue

    from ._create_statements import visitColumnCreateTable, visitCreateDefinitions, visitColumnDeclaration, visitColumnDefinition, visitUniqueKeyColumnConstraint, visitSimpleDataType
    from ._create_statements import visitIntegerDataType, visitDimensionDataType, visitLengthOneDimension, visitLengthTwoDimension, visitLengthDimensionList, visitDecimalLiteral

    from ._select_statement import visitSimpleSelect

    from ._common_clauses_ids import visitTableName, visitFullColumnName, visitSimpleId, visitDottedId

    from ._table_sources import visitTableSources, visitQuerySpecification, visitSelectElements, visitFromClause

    from ._expressions import visitStringLiteral, visitConstant, visitLogicalExpression, visitBinaryComparisonPredicate
    from ._expressions import visitNestedExpressionAtom, visitComparisonOperator, visitLogicalOperator, visitExpressionsWithDefaults

    from ._functions import visitUdfFunction, visitFunctionArgs, visitCreateUdf


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