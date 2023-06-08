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
from evadb.parser.statement import AbstractStatement
from evadb.parser.types import ObjectType, StatementType


class DropObjectStatement(AbstractStatement):

    """Drop Object Statement constructed after parsing the input query

    Attributes:
        object_type: ObjectType
        name (str
            name of the object to drop
        if_exists: bool
            if false, throws an error when no UDF with name exists
            else logs a warning
    """

    def __init__(self, object_type: ObjectType, name: str, if_exists: bool):
        super().__init__(StatementType.DROP_OBJECT)
        self._object_type = object_type
        self._name = name
        self._if_exists = if_exists

    def __str__(self) -> str:
        if self._if_exists:
            print_str = f"DROP {self._object_type} IF EXISTS {self._name};"
        else:
            print_str = f"DROP {self._object_type} {self._name};"
        return print_str

    @property
    def object_type(self):
        return self._object_type

    @property
    def name(self):
        return self._name

    @property
    def if_exists(self):
        return self._if_exists

    def __eq__(self, other):
        if not isinstance(other, DropObjectStatement):
            return False
        return (
            self.object_type == other.object_type
            and self.name == other.name
            and self.if_exists == other.if_exists
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.object_type, self.name, self.if_exists))
