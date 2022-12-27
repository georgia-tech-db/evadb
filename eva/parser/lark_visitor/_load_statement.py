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

from eva.parser.load_statement import LoadDataStatement
from eva.parser.types import FileFormatType


class Load:
    def load_statement(self, tree):
        # Set default file_format
        file_format = FileFormatType.VIDEO
        file_format = self.visit(tree.children[1])

        # Set default for file_format as Video
        file_options = {}
        file_options["file_format"] = file_format

        file_path = self.visit(tree.children[2]).value
        table = self.visit(tree.children[4])

        # set default for column_list as None
        column_list = None
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "uid_list":
                    column_list = self.visit(child)

        stmt = LoadDataStatement(table, file_path, column_list, file_options)
        return stmt

    def file_format(self, tree):
        file_format = None
        file_format_string = tree.children[0]

        if file_format_string == "VIDEO":
            file_format = FileFormatType.VIDEO
        elif file_format_string == "CSV":
            file_format = FileFormatType.CSV
        elif file_format_string == "IMAGE":
            file_format = FileFormatType.IMAGE

        return file_format

    def file_options(self, tree):
        file_options = {}
        file_format = self.visit(tree.children[1])
        file_options["file_format"] = file_format
        return file_options
