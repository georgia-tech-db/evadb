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

from lark.tree import Tree

from eva.expression.constant_value_expression import ConstantValueExpression
from eva.parser.types import ParserOrderBySortType


##################################################################
# SELECT STATEMENT
##################################################################
class Select:
    def simple_select(self, tree):
        select_stmt = self.visit_children(tree)
        return select_stmt

    def order_by_clause(self, tree):
        orderby_clause_data = []
        for child in tree.children:
            if isinstance(child, Tree):
                orderby_clause_data.append(self.visit(child))
        return orderby_clause_data

    def order_by_expression(self, tree):
        expr = None
        # default sort order
        sort_order = ParserOrderBySortType.ASC

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data.endswith("expression"):
                    expr = self.visit(child)
                elif child.data == "sort_order":
                    sort_order = self.visit(child)

        return expr, sort_order

    def sort_order(self, tree):
        token = tree.children[0]
        sort_order = None

        if token == "ASC":
            sort_order = ParserOrderBySortType.ASC
        elif token == "DESC":
            sort_order = ParserOrderBySortType.DESC
        return sort_order

    def limit_clause(self, tree):
        output = ConstantValueExpression(self.visit(tree.children[1]))
        return output
