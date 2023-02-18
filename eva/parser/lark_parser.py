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
import os

from lark import Lark

from eva.parser.lark_visitor import LarkInterpreter


class LarkParser(object):
    """
    Parser for EVA QL based on Lark
    """

    _parser = None

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(LarkParser, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        lark_path = os.path.join(dir_path, "eva.lark")
        with open(lark_path) as f:
            sql_grammar = f.read()
        self._parser = Lark(sql_grammar, parser="lalr")

    def parse(self, query_string: str) -> list:

        # remove trailing white space
        query_string = query_string.rstrip()

        # add semi-colon if needed
        if not query_string.endswith(";"):
            query_string += ";"

        tree = self._parser.parse(query_string)
        output = LarkInterpreter(query_string).visit(tree)

        # convert output to list if it is a single element
        if isinstance(output, list):
            return output
        else:
            return [output]
