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
from pprint import pprint

from lark import visitors

from eva.parser.rename_statement import RenameTableStatement
from eva.parser.table_ref import TableInfo, TableRef


class LarkInterpreter(visitors.Interpreter):
    def __init__(self, query):
        super().__init__()
        self.query = query
        pprint(query)

    def start(self, tree):
        return self.visit_children(tree)

    def sql_statement(self, tree):
        return self.visit(tree.children[0])

    def rename_table(self, tree):
        old_table_info = self.visit(tree.children[2])
        new_table_info = self.visit(tree.children[4])

        return RenameTableStatement(TableRef(old_table_info), new_table_info)

    def table_name(self, tree):
        table_name = self.visit(tree.children[0])
        return TableInfo(table_name)

    def full_id(self, tree):
        return self.visit(tree.children[0])

    def uid(self, tree):
        return self.visit(tree.children[0])

    def simple_id(self, tree):
        simple_id = str(tree.children[0])
        return simple_id
