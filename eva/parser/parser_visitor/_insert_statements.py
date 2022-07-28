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
from antlr4 import TerminalNode

from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.evaql.evaql_parser import evaql_parser
from eva.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from eva.parser.insert_statement import InsertTableStatement
from eva.parser.table_ref import TableRef


##################################################################
# INSERT STATEMENTS
##################################################################
class Insert(evaql_parserVisitor):
    def visitInsertStatement(self, ctx: evaql_parser.InsertStatementContext):
        table_ref = None
        column_list = []
        value_list = []
        # first two children with be INSERT INTO
        # Then we will have terminal nodes for '(', ')'
        for child in ctx.children[2:]:
            if not isinstance(child, TerminalNode):
                try:
                    rule_idx = child.getRuleIndex()

                    if rule_idx == evaql_parser.RULE_tableName:
                        table_ref = TableRef(self.visit(ctx.tableName()))

                    elif rule_idx == evaql_parser.RULE_uidList:
                        column_list = self.visit(ctx.uidList())

                    elif rule_idx == evaql_parser.RULE_insertStatementValue:
                        insrt_value = self.visit(ctx.insertStatementValue())
                        # Support only (value1, value2, .... value n)
                        value_list = insrt_value[0]
                except BaseException:
                    # stop parsing something bad happened
                    return None

        insert_stmt = InsertTableStatement(table_ref, column_list, value_list)
        return insert_stmt

    def visitUidList(self, ctx: evaql_parser.UidListContext):
        uid_list = []
        uid_list_length = len(ctx.uid())
        for uid_index in range(uid_list_length):
            uid = self.visit(ctx.uid(uid_index))
            uid_expr = TupleValueExpression(uid)
            uid_list.append(uid_expr)

        return uid_list

    def visitInsertStatementValue(self, ctx: evaql_parser.InsertStatementValueContext):
        insert_stmt_value = []
        for child in ctx.children:
            if not isinstance(child, TerminalNode):
                try:
                    rule_idx = child.getRuleIndex()

                    if rule_idx == evaql_parser.RULE_expressionsWithDefaults:
                        expr = self.visit(child)
                        insert_stmt_value.append(expr)

                except BaseException:
                    # stop parsing something bad happened
                    return None
        return insert_stmt_value
