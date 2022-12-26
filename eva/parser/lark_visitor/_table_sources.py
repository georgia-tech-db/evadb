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

from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.select_statement import SelectStatement
from eva.parser.table_ref import Alias, JoinNode, TableRef, TableValuedExpression
from eva.parser.types import JoinType
from eva.utils.logging_manager import logger

from lark import Tree

##################################################################
# TABLE SOURCES
##################################################################


class TableSources:

    def select_elements(self, tree):
        kind = tree.children[0]
        if kind == "*":
            select_list = [TupleValueExpression(col_name="*")]
        else:
            select_list = []
            for child in tree.children:
                element = self.visit(child)
                select_list.append(element)
        return select_list

    def table_sources(self, tree):
        return self.visit(tree.children[0])

    def table_source(self, tree):
        left_node = self.visit(tree.children[0])
        join_nodes = [left_node]
        for table_join_index in tree.children[1:]:
            table = self.visit(table_join_index)
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
    
    def table_source_item_with_sample(self, tree):
        sample_freq = None
        alias = None
        table = None

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "table_source_item":
                    table = self.visit(child)
                elif child.data == "sample_clause":
                    sample_freq = self.visit(child)
                elif child.data == "alias_clause":
                    alias = self.visit(child)

        return TableRef(table=table, alias=alias, sample_freq=sample_freq)

    def table_source_item(self, tree):
        return self.visit(tree.children[0])

    def query_specification(self, tree):
        target_list = None
        from_clause = None
        where_clause = None
        groupby_clause = None
        orderby_clause = None
        limit_count = None

        # first child is a SELECT terminal token
        for child in tree.children[1:]:
            try:
                if child.data == 'select_elements':
                    target_list = self.visit(child)
                elif child.data == 'from_clause':
                    clause = self.visit(child)
                    from_clause = clause.get("from", None)
                    where_clause = clause.get("where", None)
                    groupby_clause = clause.get("groupby", None)
                elif child.data == 'order_by_clause':
                    orderby_clause = self.visit(child)
                elif child.data == 'limit_clause':
                    limit_count = self.visit(child)

            except BaseException as e:
                # stop parsing something bad happened
                logger.error(
                    "Error while parsing \
                                QuerySpecification"
                )
                raise e

        select_stmt = SelectStatement(
            target_list,
            from_clause,
            where_clause,
            groupby_clause=groupby_clause,
            orderby_clause_list=orderby_clause,
            limit_count=limit_count,
        )

        return select_stmt

    # TODO ACTION
    def from_clause(self, tree):
        from_table = None
        where_clause = None
        groupby_clause = None
        # TODO ACTION Group By

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "table_sources":
                    from_table = self.visit(child)
                elif child.data == "where_expr":
                    where_clause = self.visit(child)
                elif child.data == "group_by_clause":
                    groupby_clause = self.visit(child)

        return {"from": from_table, "where": where_clause, "groupby": groupby_clause}

    # Join
    def inner_join(self, tree):
        table = self.visit(ctx.tableSourceItemWithSample())
        if ctx.ON() is None:
            raise Exception("ERROR: Syntax error: Join should specify the ON columns")
        join_predicates = self.visit(ctx.expression())
        return TableRef(
            JoinNode(
                None,
                table,
                predicate=join_predicates,
                join_type=JoinType.INNER_JOIN,
            )
        )

    def lateral_join(self, tree):
        tve = self.visit(ctx.tableValuedFunction())
        alias = None
        if ctx.aliasClause():
            alias = self.visit(ctx.aliasClause())
        else:
            err_msg = f"TableValuedFunction {tve.func_expr.name} should have alias."
            logger.error(err_msg)
            raise SyntaxError(err_msg)
        join_type = JoinType.LATERAL_JOIN

        return TableRef(JoinNode(None, TableRef(tve, alias=alias), join_type=join_type))

    def table_valued_function(self, tree):
        func_expr = self.visit(ctx.functionCall())
        has_unnest = False
        if ctx.UNNEST():
            has_unnest = True
        return TableValuedExpression(func_expr, do_unnest=has_unnest)

    # Nested sub query
    def subquery_table_item(self, tree):
        return self.visit(tree.children[0])

    def subquery_table_source_item(self, tree):
        subquery_table_source_item = None
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == 'simple_select':
                    subquery_table_source_item = self.visit(child)
        
        return subquery_table_source_item

    def union_select(self, tree):
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

    def group_by_clause(self, tree):
        groupby_clause = None
        if ctx.groupByItem():
            # TODO ACTION: Check what happens if 0 size is possible
            if len(ctx.groupByItem()) > 1:
                err_msg = "Parsing error: We do not \
                        support multiple attributes in GROUP BY"
                logger.error(err_msg)
                raise SyntaxError(err_msg)
            groupby_clause = self.visit(ctx.groupByItem()[0])
        return groupby_clause

    def alias_clause(self, tree):
        alias_name = None
        column_list = []

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "uid":
                    alias_name = self.visit(child)
                elif child.data == "uid_list":
                    column_list = self.visit(child)
                    column_list = [col.col_name for col in column_list]

        return Alias(alias_name, column_list)