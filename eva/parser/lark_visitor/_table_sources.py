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
                element = element[0][0][0][0]
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
        table = self.visit(tree.children[0])
        #if ctx.sampleClause():
        #    sample_freq = self.visit(ctx.sampleClause())
        #if ctx.AS():
        #    alias = Alias(self.visit(ctx.uid()))
        return TableRef(table, alias, sample_freq)

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
