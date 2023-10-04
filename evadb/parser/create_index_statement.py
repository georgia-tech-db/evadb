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
from evadb.expression.abstract_expression import AbstractExpression
from evadb.expression.function_expression import FunctionExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.create_statement import ColumnDefinition
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.parser.types import StatementType


class CreateIndexStatement(AbstractStatement):
    def __init__(
        self,
        name: str,
        if_not_exists: bool,
        table_ref: TableRef,
        col_list: List[ColumnDefinition],
        vector_store_type: VectorStoreType,
        project_expr_list: List[AbstractStatement],
    ):
        super().__init__(StatementType.CREATE_INDEX)
        self._name = name
        self._if_not_exists = if_not_exists
        self._table_ref = table_ref
        self._col_list = col_list
        self._vector_store_type = vector_store_type
        self._project_expr_list = project_expr_list

        # Definition of CREATE INDEX.
        self._index_def = self.__str__()

    def __str__(self) -> str:
        function_expr = None
        for project_expr in self._project_expr_list:
            if isinstance(project_expr, FunctionExpression):
                function_expr = project_expr

        print_str = "CREATE INDEX"
        if self._if_not_exists:
            print_str += " IF NOT EXISTS"
        print_str += f" {self._name}"
        print_str += " ON"
        print_str += f" {self._table_ref.table.table_name}"
        if function_expr is None:
            print_str += f" ({self.col_list[0].name})"
        else:

            def traverse_create_function_expression_str(expr):
                if isinstance(expr, TupleValueExpression):
                    return f"{self.col_list[0].name}"
                return f"{expr.name}({traverse_create_function_expression_str(expr.children[0])})"

            print_str += f" ({traverse_create_function_expression_str(function_expr)})"
        print_str += f" USING {self._vector_store_type};"
        return print_str

    @property
    def name(self):
        return self._name

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
    def vector_store_type(self):
        return self._vector_store_type

    @property
    def project_expr_list(self):
        return self._project_expr_list

    @project_expr_list.setter
    def project_expr_list(self, project_expr_list: List[AbstractExpression]):
        self._project_expr_list = project_expr_list

    @property
    def index_def(self):
        return self._index_def

    def __eq__(self, other):
        if not isinstance(other, CreateIndexStatement):
            return False
        return (
            self._name == other.name
            and self._if_not_exists == other.if_not_exists
            and self._table_ref == other.table_ref
            and self.col_list == other.col_list
            and self._vector_store_type == other.vector_store_type
            and self._project_expr_list == other.project_expr_list
            and self._index_def == other.index_def
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self._name,
                self._if_not_exists,
                self._table_ref,
                tuple(self.col_list),
                self._vector_store_type,
                tuple(self._project_expr_list),
                self._index_def,
            )
        )
