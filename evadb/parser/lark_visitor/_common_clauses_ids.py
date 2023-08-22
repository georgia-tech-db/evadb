# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.catalog.catalog_type import Dimension
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.table_ref import TableInfo
from evadb.utils.logging_manager import logger


class CommonClauses:
    def table_name(self, tree):
        child = self.visit(tree.children[0])
        if isinstance(child, tuple):
            database_name, table_name = child[0], child[1]
        else:
            database_name, table_name = None, child

        if table_name is not None:
            return TableInfo(table_name=table_name, database_name=database_name)
        else:
            error = "Invalid Table Name"
            logger.error(error)

    def full_id(self, tree):
        if len(tree.children) == 1:
            # Table only
            return self.visit(tree.children[0])
        elif len(tree.children) == 2:
            # Data source and table
            # Ex. DemoDB.TestTable
            return (self.visit(tree.children[0]), self.visit(tree.children[1]))

    def uid(self, tree):
        return self.visit(tree.children[0])

    def full_column_name(self, tree):
        uid = self.visit(tree.children[0])

        # check for dottedid
        if len(tree.children) > 1:
            dotted_id = self.visit(tree.children[1])
            return TupleValueExpression(table_alias=uid, name=dotted_id)
        else:
            return TupleValueExpression(name=uid)

    def dotted_id(self, tree):
        dotted_id = str(tree.children[0])
        dotted_id = dotted_id.lstrip(".")
        return dotted_id

    def simple_id(self, tree):
        simple_id = str(tree.children[0])
        return simple_id

    def decimal_literal(self, tree):
        decimal = None
        token = tree.children[0]
        if str.upper(token) == "ANYDIM":
            decimal = Dimension.ANYDIM
        else:
            decimal = int(str(token))
        return decimal

    def real_literal(self, tree):
        real_literal = float(tree.children[0])
        return real_literal
