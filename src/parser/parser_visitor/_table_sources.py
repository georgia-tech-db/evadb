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

from src.parser.select_statement import SelectStatement
from src.parser.table_ref import JoinNode
from src.parser.table_ref import TableRef

from src.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from src.parser.evaql.evaql_parser import evaql_parser
from src.parser.types import ParserOrderBySortType
from src.parser.types import JoinType
from src.expression.constant_value_expression import ConstantValueExpression

##################################################################
# TABLE SOURCES
##################################################################


class TableSources(evaql_parserVisitor):
    def visitTableSources(self, ctx: evaql_parser.TableSourcesContext):

        table_list = []
        table_sources_count = len(ctx.tableSource())

        for table_sources_index in range(table_sources_count):
            table = self.visit(ctx.tableSource(table_sources_index))
            table_list.append(table)

        # Join Nodes
        if table_sources_count > 1:
            # merge join nodes
            # table, join_node1, join_node2 -> join_node_1, join_node_2
            for i in range(table_sources_count - 1):
                table_list[i + 1].join.left = table_list[i]
            table_list = table_list[1:]

        return table_list

    def visitSubqueryTableItem(
            self, ctx: evaql_parser.SubqueryTableItemContext):
        table_ref = self.visit(ctx.subqueryTableSourceItem())
        # Lateral Join
        if ctx.LATERAL():
            return TableRef(join=JoinNode(right=table_ref,
                                          join_type=JoinType.LATERAL_JOIN))

        return table_ref

    def visitSubqueryTableSourceItem(
            self, ctx: evaql_parser.SubqueryTableSourceItemContext):
        if ctx.selectStatement():
            return self.visit(ctx.selectStatement())
        else:
            return self.visit(ctx.functionCall())

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
        orderby_clause = None
        limit_count = None

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

                elif rule_idx == evaql_parser.RULE_orderByClause:
                    orderby_clause = self.visit(ctx.orderByClause())

                elif rule_idx == evaql_parser.RULE_limitClause:
                    limit_count = self.visit(ctx.limitClause())

            except BaseException:
                # stop parsing something bad happened
                return None

        # we don't support multiple table sources
        if from_clause is not None:
            from_clause = from_clause[0]

        select_stmt = SelectStatement(
            target_list, from_clause, where_clause,
            orderby_clause_list=orderby_clause,
            limit_count=limit_count)

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

    def visitOrderByClause(self, ctx: evaql_parser.OrderByClauseContext):
        orderby_clause_data = []
        # [(TupleValueExpression #1, ASC), (TVE #2, DESC), ...]
        for expression in ctx.orderByExpression():
            orderby_clause_data.append(self.visit(expression))

        return orderby_clause_data

    def visitOrderByExpression(
            self, ctx: evaql_parser.OrderByExpressionContext):

        if ctx.DESC():
            sort_token = ParserOrderBySortType.DESC
        else:
            sort_token = ParserOrderBySortType.ASC

        return self.visitChildren(ctx.expression()), sort_token

    def visitLimitClause(self, ctx: evaql_parser.LimitClauseContext):
        return ConstantValueExpression(self.visitChildren(ctx))
