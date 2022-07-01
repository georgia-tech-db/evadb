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

from eva.parser.select_statement import SelectStatement
from eva.parser.table_ref import TableRef, JoinNode

from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.types import JoinType
from eva.utils.logging_manager import logger

##################################################################
# TABLE SOURCES
##################################################################


class TableSources(evaql_parserVisitor):
    def visitTableSources(self, ctx: evaql_parser.TableSourcesContext):
        return self.visit(ctx.tableSource())

    def visitTableSourceBase(self, ctx: evaql_parser.TableSourceBaseContext):
        left_node = self.visit(ctx.tableSourceItemWithSample())
        join_nodes = [left_node]
        for table_join_index in range(len(ctx.joinPart())):
            table = self.visit(ctx.joinPart(table_join_index))
            join_nodes.append(table)

        num_table_joins = len(join_nodes)

        # Join Nodes
        if num_table_joins > 1:
            # Add Join nodes -> left deep tree
            # t1, t2, t3 -> j2 ( j1 ( t1, t2 ), t3 )
            for i in range(num_table_joins - 1):
                join_nodes[i + 1].join_node.left = join_nodes[i]

            return join_nodes[-1]
        else:
            return join_nodes[0]

    # Join
    def visitInnerJoin(self, ctx: evaql_parser.InnerJoinContext):
        table = self.visit(ctx.tableSourceItemWithSample())
        if table.is_func_expr():
            return TableRef(JoinNode(None,
                                     table,
                                     join_type=JoinType.LATERAL_JOIN))
        else:
            if ctx.ON() is None:
                raise Exception(
                    'ERROR: Syntax error: Join should specify the ON columns')
            join_predicates = self.visit(ctx.expression())
            return TableRef(JoinNode(None,
                                     table,
                                     predicate=join_predicates,
                                     join_type=JoinType.INNER_JOIN))

    def visitTableSourceItemWithSample(
            self, ctx: evaql_parser.TableSourceItemWithSampleContext):
        sample_freq = None
        alias = None
        table = self.visit(ctx.tableSourceItem())
        if ctx.sampleClause():
            sample_freq = self.visit(ctx.sampleClause())
        if ctx.AS():
            alias = self.visit(ctx.uid())
        return TableRef(table, alias, sample_freq)

    # Nested sub query
    def visitSubqueryTableItem(
            self, ctx: evaql_parser.SubqueryTableItemContext):
        return self.visit(ctx.subqueryTableSourceItem())

    def visitLateralFunctionCallItem(
            self, ctx: evaql_parser.LateralFunctionCallItemContext):
        return self.visit(ctx.functionCall())

    def visitSubqueryTableSourceItem(
            self, ctx: evaql_parser.SubqueryTableSourceItemContext):
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

            except BaseException as e:
                # stop parsing something bad happened
                logger.error('Error while parsing \
                                visitQuerySpecification')
                raise e

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
