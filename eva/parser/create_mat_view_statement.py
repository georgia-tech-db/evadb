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
from typing import List

from eva.parser.create_statement import ColumnDefinition
from eva.parser.select_statement import SelectStatement
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.parser.types import StatementType


class CreateMaterializedViewStatement(AbstractStatement):
    """Create Materialized View Statement constructed after parsing the input query
    Attributes:
        view_ref: table reference to store the view
        if_not_exists: if true overwrite any existing view, else throw an error
        query: select statement used to populate the view
    """

    def __init__(
        self,
        view_ref: TableRef,
        col_list: List[ColumnDefinition],
        if_not_exists: bool,
        query: SelectStatement,
    ):
        super().__init__(StatementType.CREATE_MATERIALIZED_VIEW)
        self._view_ref = view_ref
        self._col_list = col_list
        self._if_not_exists = if_not_exists
        self._query = query

    def __str__(self) -> str:
        print_str = "CREATE MATERIALIZED VIEW {} ({}) AS {} ".format(
            self._view_ref, self._col_list, self._query
        )
        return print_str

    @property
    def view_ref(self):
        return self._view_ref

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def query(self):
        return self._query

    @property
    def col_list(self):
        return self._col_list

    def __eq__(self, other):
        if not isinstance(other, CreateMaterializedViewStatement):
            return False
        return (
            self.view_ref == other.view_ref
            and self.col_list == other.col_list
            and self.if_not_exists == other.if_not_exists
            and self.query == other.query
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.view_ref,
                tuple(self.col_list),
                self.if_not_exists,
                self.query,
            )
        )
