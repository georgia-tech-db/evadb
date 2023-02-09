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

from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.insert_statement import InsertTableStatement
from eva.parser.table_ref import TableRef


##################################################################
# INSERT STATEMENTS
##################################################################
class Insert:
    def insert_statement(self, tree):
        table_ref = None
        column_list = []
        value_list = []

        # print(tree.pretty())

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "table_name":
                    table_name = self.visit(child)
                    table_ref = TableRef(table_name)
                elif child.data == "uid_list":
                    column_list = self.visit(child)
                elif child.data == "insert_statement_value":
                    insrt_value = self.visit(child)
                    # Support only (value1, value2, .... value n)
                    value_list = insrt_value[0]

        insert_stmt = InsertTableStatement(table_ref, column_list, value_list)
        return insert_stmt

    def uid_list(self, tree):
        uid_expr_list = []
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "uid":
                    uid = self.visit(child)
                    uid_expr = TupleValueExpression(uid)
                    uid_expr_list.append(uid_expr)

        return uid_expr_list

    def insert_statement_value(self, tree):
        insert_stmt_value = []

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "expressions_with_defaults":
                    expr = self.visit(child)
                    insert_stmt_value.append(expr)

        return insert_stmt_value
