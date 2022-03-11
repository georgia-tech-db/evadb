# coding=utf-8
# Copyright 2018-2020 EVA
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


class UpdateStatement(AbstractStatement):
    """
    Update Statement constructed after parsing the input query

    Arguments:
        table_name(str): the name of the target table
        updated_element(expression): expression(s) of the updated element.
        condition_expression(expression): an expression of the condition
    """

    def __init__(self, table_name: str, updated_element: str, condition_expression: str):
        super().__init__(StatementType.UPDATE)
        self._table_name = table_name
        self._updated_element = updated_element
        self._condition_expression = condition_expression

    def __str__(self) -> str:
        print_str = "UPDATE {} SET {} WHERE {}".format(
            self._table_name, self._updated_element, self._condition_expression)
        return print_str

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def updated_element(self) -> str:
        return self._updated_element

    @property
    def condition_expression(self) -> str:
        return self._condition_expression

    def __eq__(self, other):
        if not isinstance(other, UpdateStatement):
            return False
        return (self.table_name == other.table_name and
                self.updated_element == other.updated_element and
                self.condition_expression == other.condition_expression)
