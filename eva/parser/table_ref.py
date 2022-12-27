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
from __future__ import annotations

from typing import Union

from eva.expression.abstract_expression import AbstractExpression
from eva.expression.function_expression import FunctionExpression
from eva.parser.alias import Alias
from eva.parser.select_statement import SelectStatement
from eva.parser.types import JoinType


class TableInfo:
    """
    stores all the table info, inspired from postgres
    """

    def __init__(self, table_name=None, schema_name=None, database_name=None):
        self._table_name = table_name
        self._schema_name = schema_name
        self._database_name = database_name
        self._table_obj = None

    @property
    def table_name(self):
        return self._table_name

    @property
    def schema_name(self):
        return self._schema_name

    @property
    def database_name(self):
        return self._database_name

    @property
    def table_obj(self):
        return self._table_obj

    @table_obj.setter
    def table_obj(self, obj):
        self._table_obj = obj

    def __str__(self):
        table_info_str = self._table_name

        return table_info_str

    def __eq__(self, other):
        if not isinstance(other, TableInfo):
            return False
        return (
            self.table_name == other.table_name
            and self.schema_name == other.schema_name
            and self.database_name == other.database_name
            and self.table_obj == other.table_obj
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.table_name,
                self.schema_name,
                self.database_name,
                self.table_obj,
            )
        )


class JoinNode:
    def __init__(
        self,
        left: "TableRef" = None,
        right: "TableRef" = None,
        predicate: AbstractExpression = None,
        join_type: JoinType = None,
    ) -> None:
        self.left = left
        self.right = right
        self.predicate = predicate
        self.join_type = join_type

    def __eq__(self, other):
        if not isinstance(other, JoinNode):
            return False
        return (
            self.left == other.left
            and self.right == other.right
            and self.predicate == other.predicate
            and self.join_type == other.join_type
        )

    def __str__(self) -> str:
        return "JOIN {} ({}, {}) ON {}".format(
            self.join_type, self.left, self.right, self.predicate
        )


class TableValuedExpression:
    def __init__(self, func_expr: FunctionExpression, do_unnest: bool = False) -> None:
        self._func_expr = func_expr
        self._do_unnest = do_unnest

    @property
    def func_expr(self):
        return self._func_expr

    @property
    def do_unnest(self):
        return self._do_unnest

    def __eq__(self, other):
        if not isinstance(other, TableValuedExpression):
            return False
        return self.func_expr == other.func_expr and self.do_unnest == other.do_unnest

    def __hash__(self) -> int:
        return hash((self.func_expr, self.do_unnest))


class TableRef:
    """
    Attributes:
        : can be one of the following based on the query type:
            TableInfo: expression of table name and database name,
            TableValuedExpression: lateral function calls
            SelectStatement: select statement in case of nested queries,
            JoinNode: join node in case of join queries
        sample_freq: sampling frequency for the table reference
    """

    def __init__(
        self,
        table: Union[TableInfo, TableValuedExpression, SelectStatement, JoinNode],
        alias: Alias = None,
        sample_freq: float = None,
    ):

        self._ref_handle = table
        self._sample_freq = sample_freq
        self.alias = alias or self.generate_alias()

    @property
    def sample_freq(self):
        return self._sample_freq

    def is_table_atom(self) -> bool:
        return isinstance(self._ref_handle, TableInfo)

    def is_table_valued_expr(self) -> bool:
        return isinstance(self._ref_handle, TableValuedExpression)

    def is_select(self) -> bool:
        return isinstance(self._ref_handle, SelectStatement)

    def is_join(self) -> bool:
        return isinstance(self._ref_handle, JoinNode)

    @property
    def table(self) -> TableInfo:
        assert isinstance(
            self._ref_handle, TableInfo
        ), "Expected \
                TableInfo, got {}".format(
            type(self._ref_handle)
        )
        return self._ref_handle

    @property
    def table_valued_expr(self) -> TableValuedExpression:
        assert isinstance(
            self._ref_handle, TableValuedExpression
        ), "Expected \
                TableValuedExpression, got {}".format(
            type(self._ref_handle)
        )
        return self._ref_handle

    @property
    def join_node(self) -> JoinNode:
        assert isinstance(
            self._ref_handle, JoinNode
        ), "Expected \
                JoinNode, got {}".format(
            type(self._ref_handle)
        )
        return self._ref_handle

    @property
    def select_statement(self) -> SelectStatement:
        assert isinstance(
            self._ref_handle, SelectStatement
        ), "Expected \
                SelectStatement, got{}".format(
            type(self._ref_handle)
        )
        return self._ref_handle

    def generate_alias(self) -> str:
        # create alias for the table
        # TableInfo -> table_name.lower()
        # SelectStatement -> select
        if isinstance(self._ref_handle, TableInfo):
            return Alias(self._ref_handle.table_name.lower())
        elif isinstance(self._ref_handle, SelectStatement):
            raise RuntimeError("Nested select should have alias")

    def __str__(self):
        table_ref_str = "TABLE REF:: ( {} SAMPLE FREQUENCY {})".format(
            str(self._ref_handle), str(self.sample_freq)
        )
        return table_ref_str

    def __eq__(self, other):
        if not isinstance(other, TableRef):
            return False
        return (
            self._ref_handle == other._ref_handle
            and self.alias == other.alias
            and self.sample_freq == other.sample_freq
        )

    def __hash__(self) -> int:
        return hash((self._ref_handle, self.alias, self.sample_freq))
