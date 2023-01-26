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
from eva.parser.delete_statement import DeleteTableStatement
from eva.parser.table_ref import TableRef


##################################################################
# DELETE STATEMENTS
##################################################################
class Delete:
    def delete_statement(self, tree):
        table_ref = None
        where_clause = None
        order_clause = None
        limit_count = None
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "table_name":
                    table_name = self.visit(child)
                    table_ref = TableRef(table_name)
                elif child.data == "where_expr":
                    where_clause = self.visit(child)
                elif child.data == "order_by_clause":
                    order_clause = self.visit(child)
                elif child.data == "limit_clause":
                    limit_count = self.visit(child)
                    
        delete_stmt = DeleteTableStatement(table_ref, where_clause, order_clause, limit_count)
        return delete_stmt

    
