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

from eva.parser.overwrite_statement import OverwriteStatement


class Overwrite:
    def overwrite_statement(self, tree):
        table_info = None
        operation = None

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "table_name":
                    table_info = self.visit(child)
                elif child.data == "operation":
                    operation = self.visit(child).value

        stmt = OverwriteStatement(table_info, operation)
        return stmt
