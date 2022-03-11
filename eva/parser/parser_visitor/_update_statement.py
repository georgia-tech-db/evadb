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

from eva.parser.update_statement import UpdateStatement
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.evaql.evaql_parser import evaql_parser


class Update(evaql_parserVisitor):
    def visitUpdateStatement(self, ctx: evaql_parser.UpdateStatementContext):
        table_name = self.visit(ctx.tableName()).value
        updated_element = self.visit(ctx.updatedElement()).value
        condition_expression = self.visit(ctx.expression()).value
        stmt = UpdateStatement(table_name, updated_element, condition_expression)
        return stmt