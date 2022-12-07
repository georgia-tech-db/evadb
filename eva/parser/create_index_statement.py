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
from pathlib import Path
from typing import List

from eva.expression.abstract_expression import AbstractExpression
from eva.parser.statement import AbstractStatement
from eva.parser.table_ref import TableRef
from eva.parser.types import StatementType
from eva.catalog.column_type import FaissIndexType


class CreateIndexStatement(AbstractStatement):
    """Create Index Statement constructed after parsing the input query

    Attributes:
        index_name: str
            index_name provided by the user required
        if_not_exists: bool
            if true should throw an error if udf with same name exists
            else will replace the existing
        table_name: str
            on which table the index will be created.
        col_list: List[AbstractExpression]
            on which columns the index will be created.
    """

    def __init__(
        self,
        index_name: str,
        if_not_exists: bool,
        table_ref: TableRef,
        col_list: List[AbstractExpression] = None,
        faiss_idx_type: FaissIndexType = None
    ):
        super().__init__(StatementType.CREATE_INDEX)
        self._index_name = index_name
        self._if_not_exists = if_not_exists
        self._table_ref = table_ref
        self._col_list = col_list
        self._faiss_idx_type = faiss_idx_type

    def __str__(self) -> str:
        print_str = "CREATE INDEX {} ON {}({})".format(
            self._index_name,
            self._table_ref,
            self._col_list
        )
        return print_str

    @property
    def index_name(self):
        return self._index_name

    @property
    def if_not_exists(self):
        return self._if_not_exists

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def col_list(self):
        return self._col_list

    @property
    def faiss_idx_type(self):
        return self._faiss_idx_type

    def __eq__(self, other):
        if not isinstance(other, CreateIndexStatement):
            return False
        return (
            self._index_name == other._index_name
            and self.if_not_exists == other.if_not_exists
            and self._table_ref == other._table_ref
            and self._col_list == other._col_list
            and self._faiss_idx_type == other._faiss_idx_type
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self._index_name,
                self.if_not_exists,
                self._table_ref,
                self._faiss_idx_type,
                tuple(self._col_list)
            )
        )
