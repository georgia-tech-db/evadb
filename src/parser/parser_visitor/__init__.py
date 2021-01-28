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

from antlr4 import TerminalNode
from src.parser.evaql.evaql_parser import evaql_parser

from src.parser.parser_visitor._common_clauses_ids import CommonClauses
from src.parser.parser_visitor._create_statements import CreateTable
from src.parser.parser_visitor._expressions import Expressions
from src.parser.parser_visitor._functions import Functions
from src.parser.parser_visitor._insert_statements import Insert
from src.parser.parser_visitor._select_statement import Select
from src.parser.parser_visitor._table_sources import TableSources
from src.parser.parser_visitor._load_statement import Load

# To add new functionality to the parser, create a new file under
# the parser_visitor directory, and implement a new class which
# overloads the required visitors' functions.
# Then make the new class as a parent class for ParserVisitor.


class ParserVisitor(CommonClauses, CreateTable, Expressions,
                    Functions, Insert, Select, TableSources,
                    Load):
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
