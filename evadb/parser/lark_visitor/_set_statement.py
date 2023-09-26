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
from lark.tree import Tree

from evadb.parser.set_statement import SetStatement


##################################################################
# DELETE STATEMENTS
##################################################################
class Set:
    def set_statement(self, tree):
        config_name = None
        config_value = None
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data == "config_name":
                    config_name = self.visit(child)
                elif child.data == "config_value":
                    config_value = self.visit(child)

        set_stmt = SetStatement(config_name, config_value)
        return set_stmt
