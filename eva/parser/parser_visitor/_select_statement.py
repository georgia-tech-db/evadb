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
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.types import ParserOrderBySortType


##################################################################
# SELECT STATEMENT
##################################################################
class Select(evaql_parserVisitor):
    def visitSimpleSelect(self, ctx: evaql_parser.SimpleSelectContext):
        select_stmt = self.visitChildren(ctx)
        return select_stmt

    def visitOrderByClause(self, ctx: evaql_parser.OrderByClauseContext):
        orderby_clause_data = []
        # [(TupleValueExpression #1, ASC), (TVE #2, DESC), ...]
        for expression in ctx.orderByExpression():
            orderby_clause_data.append(self.visit(expression))

        return orderby_clause_data

    def visitOrderByExpression(self, ctx: evaql_parser.OrderByExpressionContext):

        if ctx.DESC():
            sort_token = ParserOrderBySortType.DESC
        else:
            sort_token = ParserOrderBySortType.ASC

        return self.visitChildren(ctx.expression()), sort_token

    def visitLimitClause(self, ctx: evaql_parser.LimitClauseContext):
        return ConstantValueExpression(self.visitChildren(ctx))
