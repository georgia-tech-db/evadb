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
from eva.parser.select_statement import SelectStatement
from eva.parser.semantic_statement import SemanticStatement

class Semantic:
    def semantic_search_statement(self, tree):
        select_stmt = SelectStatement()
        semantic_stmt = SemanticStatement(tree.children[1].value, select_stmt)
        return semantic_stmt