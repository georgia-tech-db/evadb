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
from lark import Tree

from evadb.parser.drop_object_statement import DropObjectStatement
from evadb.parser.types import ObjectType


class DropObject:
    def drop_table(self, tree):
        table_name = None
        if_exists = False

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "if_exists":
                    if_exists = True
                elif child.data == "uid":
                    table_name = self.visit(child)

        return DropObjectStatement(ObjectType.TABLE, table_name, if_exists)

    # Drop Index
    def drop_index(self, tree):
        index_name = None
        if_exists = False

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "if_exists":
                    if_exists = True
                elif child.data == "uid":
                    index_name = self.visit(child)

        return DropObjectStatement(ObjectType.INDEX, index_name, if_exists)

    # Drop Function
    def drop_function(self, tree):
        function_name = None
        if_exists = False

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "uid":
                    function_name = self.visit(child)
                elif child.data == "if_exists":
                    if_exists = True

        return DropObjectStatement(ObjectType.FUNCTION, function_name, if_exists)

    # Drop Database
    def drop_database(self, tree):
        database_name = None
        if_exists = False

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "if_exists":
                    if_exists = True
                elif child.data == "uid":
                    database_name = self.visit(child)

        return DropObjectStatement(ObjectType.DATABASE, database_name, if_exists)
