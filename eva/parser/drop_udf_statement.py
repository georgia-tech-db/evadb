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
from eva.parser.statement import AbstractStatement
from eva.parser.types import StatementType


class DropUDFStatement(AbstractStatement):
    """Drop UDF Statement constructed after parsing the input query

    Attributes:
        name: str
            name of the udf
        if_exists: bool
            if false, throws an error when no UDF with name exists
            else logs a warning
    """

    def __init__(self, name: str, if_exists: bool):
        super().__init__(StatementType.DROP_UDF)
        self._name = name
        self._if_exists = if_exists

    def __str__(self) -> str:
        if self._if_exists:
            print_str = "DROP UDF IF EXISTS {};".format(self._name)
        else:
            print_str = "DROP UDF {};".format(self._name)
        return print_str

    @property
    def name(self):
        return self._name

    @property
    def if_exists(self):
        return self._if_exists

    def __eq__(self, other):
        if not isinstance(other, DropUDFStatement):
            return False
        return self.name == other.name and self.if_exists == other.if_exists

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.name, self.if_exists))
