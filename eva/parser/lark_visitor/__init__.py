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
from typing import List, TypeVar

from lark import Tree, visitors

from eva.parser.lark_visitor._common_clauses_ids import CommonClauses
from eva.parser.lark_visitor._create_statements import CreateTable
from eva.parser.lark_visitor._drop_statement import DropTable
from eva.parser.lark_visitor._explain_statement import Explain
from eva.parser.lark_visitor._expressions import Expressions
from eva.parser.lark_visitor._functions import Functions
from eva.parser.lark_visitor._insert_statements import Insert
from eva.parser.lark_visitor._load_statement import Load
from eva.parser.lark_visitor._rename_statement import RenameTable
from eva.parser.lark_visitor._select_statement import Select
from eva.parser.lark_visitor._show_statements import Show
from eva.parser.lark_visitor._table_sources import TableSources
from eva.parser.lark_visitor._upload_statement import Upload

# To add new functionality to the parser, create a new file under
# the lark_visitor directory, and implement a new class which
# overloads the required visitors' functions.
# Then make the new class as a parent class for ParserVisitor.

_Leaf_T = TypeVar("_Leaf_T")


class LarkBaseInterpreter(visitors.Interpreter):
    # Override default behavior of Interpreter
    def visit_children(self, tree: Tree[_Leaf_T]) -> List:

        output = [
            self._visit_tree(child) if isinstance(child, Tree) else child
            for child in tree.children
        ]

        # special case to flatten list
        if len(output) == 1:
            output = output[0]

        return output


# Modified, add RenameTable
class LarkInterpreter(
    LarkBaseInterpreter,
    CommonClauses,
    CreateTable,
    Expressions,
    Functions,
    Insert,
    Select,
    TableSources,
    Load,
    Upload,
    RenameTable,
    DropTable,
    Show,
    Explain,
):
    def __init__(self, query):
        super().__init__()
        self.query = query

    def start(self, tree):
        return self.visit_children(tree)

    def sql_statement(self, tree):
        return self.visit(tree.children[0])
