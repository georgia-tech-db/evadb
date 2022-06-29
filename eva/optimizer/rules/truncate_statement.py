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
from eva.parser.table_ref import TableRef


class TruncateTableStatement(AbstractStatement):
    """Truncate Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the truncate table statement
    """

    def __init__(self,
                 table_ref: TableRef):
        super().__init__(StatementType.TRUNCATE)
        self._table_ref = table_ref

    def __str__(self) -> str:
        print_str = "TRUNCATE TABLE {}".format(self._table_ref)
        return print_str

    @property
    def table_ref(self):
        return self._table_ref

    def __eq__(self, other):
        if not isinstance(other, TruncateTableStatement):
            return False
        return (self.table_ref == other.table_ref)
        # and self.if_exists == other.if_exists)
