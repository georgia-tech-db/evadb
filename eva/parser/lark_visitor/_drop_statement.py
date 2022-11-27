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
from eva.parser.drop_statement import DropTableStatement
from eva.parser.table_ref import TableRef


class DropTable:
    def tables(self, tree):
        tables = []
        for child in ctx.children:
            tables.append(TableRef(self.visit(child)))
        return tables

    def drop_table(self, tree):
        # table_ref = None
        if_exists = False
        for child in ctx.children[2:]:
            if child.getRuleIndex() == evaql_parser.RULE_ifExists:
                if_exists = True
        tables_to_drop = self.visit(ctx.tables())

        drop_stmt = DropTableStatement(tables_to_drop, if_exists=if_exists)
        return drop_stmt
