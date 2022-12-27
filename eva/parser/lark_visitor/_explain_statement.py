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

from eva.parser.explain_statement import ExplainStatement


class Explain:
    def explain_statement(self, tree):
        explainable_stmt = None

        for child in tree.children:
            if isinstance(child, Tree):
                if child.data.endswith("explainable_statement"):
                    explainable_stmt = self.visit(child)

        return ExplainStatement(explainable_stmt)
