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
from typing import List

from evadb.catalog.catalog_type import VectorStoreType
from evadb.expression.function_expression import FunctionExpression
from evadb.parser.create_statement import ColumnDefinition
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.parser.types import StatementType


class CreateIndexStatement(AbstractStatement):
    def __init__(
        self,
        name: str,
        table_ref: TableRef,
        col_list: List[ColumnDefinition],
        vector_store_type: VectorStoreType,
        udf_func: FunctionExpression = None,
    ):
        super().__init__(StatementType.CREATE_INDEX)
        self._name = name
        self._table_ref = table_ref
        self._col_list = col_list
        self._vector_store_type = vector_store_type
        self._udf_func = udf_func

    def __str__(self) -> str:
        print_str = "CREATE INDEX {} ON {} ({}{}) ".format(
            self._name,
            self._table_ref,
            "" if self._udf_func else self._udf_func,
            tuple(self._col_list),
        )
        return print_str

    @property
    def name(self):
        return self._name

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def col_list(self):
        return self._col_list

    @property
    def vector_store_type(self):
        return self._vector_store_type

    @property
    def udf_func(self):
        return self._udf_func

    def __eq__(self, other):
        if not isinstance(other, CreateIndexStatement):
            return False
        return (
            self._name == other.name
            and self._table_ref == other.table_ref
            and self.col_list == other.col_list
            and self._vector_store_type == other.vector_store_type
            and self._udf_func == other.udf_func
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self._name,
                self._table_ref,
                tuple(self.col_list),
                self._vector_store_type,
                self._udf_func,
            )
        )
