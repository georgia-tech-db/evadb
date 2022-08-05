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
from eva.parser.table_ref import TableInfo, TableRef
from eva.parser.types import StatementType

#  Modified


class RenameTableStatement(AbstractStatement):
    """Rename Table Statement constructed after parsing the input query

    Attributes:
        old_table_ref: table reference in the rename table statement
        new_table_name: new name of the table
    """

    def __init__(self, old_table_ref: TableRef, new_table_name: TableInfo):
        super().__init__(StatementType.RENAME)
        self._old_table_ref = old_table_ref
        self._new_table_name = new_table_name

    def __str__(self) -> str:
        print_str = "RENAME TABLE {} TO {} ".format(
            self._old_table_ref, self._new_table_name
        )
        return print_str

    @property
    def old_table_ref(self):
        return self._old_table_ref

    @property
    def new_table_name(self):
        return self._new_table_name

    def __eq__(self, other):
        if not isinstance(other, RenameTableStatement):
            return False
        return (
            self.old_table_ref == other.old_table_ref
            and self.new_table_name == other.new_table_name
        )
