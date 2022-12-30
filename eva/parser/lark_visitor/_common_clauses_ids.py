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

from eva.catalog.catalog_type import Dimension
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.table_ref import TableInfo
from eva.utils.logging_manager import logger


class CommonClauses:
    def table_name(self, tree):
        table_name = self.visit(tree.children[0])
        if table_name is not None:
            return TableInfo(table_name=table_name)
        else:
            error = "Invalid Table Name"
            logger.error(error)

    def full_id(self, tree):
        return self.visit(tree.children[0])

    def uid(self, tree):
        return self.visit(tree.children[0])

    def full_column_name(self, tree):
        uid = self.visit(tree.children[0])

        # check for dottedid
        if len(tree.children) > 1:
            dotted_id = self.visit(tree.children[1])
            return TupleValueExpression(table_alias=uid, col_name=dotted_id)
        else:
            return TupleValueExpression(col_name=uid)

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
        if token == "ANYDIM":
            decimal = Dimension.ANYDIM
        else:
            decimal = int(str(token))
        return decimal

    def real_literal(self, tree):
        real_literal = float(tree.children[0])
        return real_literal
