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
from lark import Tree

from eva.parser.drop_statement import DropTableStatement


class DropTable:
    def drop_table(self, tree):
        table_info = None
        if_exists = False

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "if_exists":
                    if_exists = True
                elif child.data == "table_name":
                    table_info = self.visit(child)

        # Need to wrap table in a list
        table_info_list = [table_info]

        drop_stmt = DropTableStatement(table_info_list, if_exists)
        return drop_stmt
