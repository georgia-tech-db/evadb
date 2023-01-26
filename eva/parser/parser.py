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
from eva.parser.lark_parser import LarkParser


class Parser(object):
    """
    Parser based on EVAQL grammar: eva.lark
    """

    _lark_parser = None

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Parser, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._lark_parser = LarkParser()
        self._initialized = True

    def parse(self, query_string: str) -> list:

        lark_output = self._lark_parser.parse(query_string)
        return lark_output
