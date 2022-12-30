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

import typing
from typing import List, Union

if typing.TYPE_CHECKING:
    from eva.parser.table_ref import TableRef

from eva.expression.abstract_expression import AbstractExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.parser.statement import AbstractStatement
from eva.parser.types import ParserOrderBySortType, StatementType


class SelectStatement(AbstractStatement):
    """
    Select Statement constructed after parsing the input query

    Attributes
    ----------
    _target_list : List[AbstractExpression]
        list of target attributes in the select query,
        each attribute is represented as a Abstract Expression
    _from_table : TableRef | Select Statement
        table reference in the select query, can be a select statement
        in nested queries
    _where_clause : AbstractExpression
        predicate of the select query, represented as a expression tree.
    **kwargs : to support other functionality, Orderby, Distinct, Groupby.
    """

    def __init__(
        self,
        target_list: List[AbstractExpression] = None,
        from_table: Union[TableRef, SelectStatement] = None,
        where_clause: AbstractExpression = None,
        **kwargs,
    ):
        super().__init__(StatementType.SELECT)
        self._from_table = from_table
        self._where_clause = where_clause
        self._target_list = target_list
        self._union_link = None
        self._union_all = False
        self._groupby_clause = kwargs.get("groupby_clause", None)
        self._orderby_list = kwargs.get("orderby_clause_list", None)
        self._limit_count = kwargs.get("limit_count", None)

    @property
    def union_link(self):
        return self._union_link

    @union_link.setter
    def union_link(self, next_select: "SelectStatement"):
        self._union_link = next_select

    @property
    def union_all(self):
        return self._union_all

    @union_all.setter
    def union_all(self, all: bool):
        self._union_all = all

    @property
    def where_clause(self):
        return self._where_clause

    @where_clause.setter
    def where_clause(self, where_expr: AbstractExpression):
        self._where_clause = where_expr

    @property
    def target_list(self):
        return self._target_list

    @target_list.setter
    def target_list(self, target_expr_list: List[AbstractExpression]):
        self._target_list = target_expr_list

    @property
    def from_table(self):
        return self._from_table

    @from_table.setter
    def from_table(self, table: TableRef):
        self._from_table = table

    @property
    def groupby_clause(self):
        return self._groupby_clause

    @groupby_clause.setter
    def groupby_clause(self, groupby_expr: AbstractExpression):
        self._groupby_clause = groupby_expr

    @property
    def orderby_list(self):
        return self._orderby_list

    @orderby_list.setter
    def orderby_list(self, orderby_list_new):
        # orderby_list_new: List[(TupleValueExpression, int)]
        self._orderby_list = orderby_list_new

    @property
    def limit_count(self):
        return self._limit_count

    @limit_count.setter
    def limit_count(self, limit_count_new: ConstantValueExpression):
        self._limit_count = limit_count_new

    def __str__(self) -> str:

        target_list_str = ""
        if self._target_list is not None:
            for expr in self._target_list:
                target_list_str += str(expr) + ", "
            target_list_str = target_list_str.rstrip(", ")

        orderby_list_str = ""
        if self._orderby_list is not None:
            for expr in self._orderby_list:
                sort_str = ""
                if expr[1] == ParserOrderBySortType.ASC:
                    sort_str = "ASC"
                elif expr[1] == ParserOrderBySortType.DESC:
                    sort_str = "DESC"
                orderby_list_str += str(expr[0]) + " " + sort_str + ", "
            orderby_list_str = orderby_list_str.rstrip(", ")

        select_str = f"SELECT {target_list_str} FROM {str(self._from_table)}"

        if self._where_clause is not None:
            select_str += " WHERE " + str(self._where_clause)

        if self._union_link is not None:
            if not self._union_all:
                select_str += " UNION " + str(self._union_link)
            else:
                select_str += " UNION ALL " + str(self._union_link)

        if self._groupby_clause is not None:
            select_str += " GROUP BY " + str(self._groupby_clause)

        if self._orderby_list is not None:
            select_str += " ORDER BY " + orderby_list_str

        if self._limit_count is not None:
            select_str += " LIMIT " + str(self._limit_count)

        select_str = select_str.rstrip(" ")

        return select_str

    def __eq__(self, other):
        if not isinstance(other, SelectStatement):
            return False
        return (
            self.from_table == other.from_table
            and self.target_list == other.target_list
            and self.where_clause == other.where_clause
            and self.union_link == other.union_link
            and self.union_all == other.union_all
            and self._groupby_clause == other.groupby_clause
            and self.orderby_list == other.orderby_list
            and self.limit_count == other.limit_count
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.from_table,
                tuple(self.target_list or []),
                self.where_clause,
                self.union_link,
                self.union_all,
                self.groupby_clause,
                tuple(self.orderby_list or []),
                self.limit_count,
            )
        )
