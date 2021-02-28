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

from src.parser.types import TableRefType
from src.parser.types import JoinType
from src.expression.abstract_expression import AbstractExpression


class TableInfo:
    """
    stores all the table info, inspired from postgres
    """

    def __init__(self, table_name=None, schema_name=None, database_name=None):
        self._table_name = table_name
        self._schema_name = schema_name
        self._database_name = database_name

    @property
    def table_name(self):
        return self._table_name

    @property
    def schema_name(self):
        return self._schema_name

    @property
    def database_name(self):
        return self._database_name

    def __str__(self):
        table_info_str = "TABLE INFO:: (" + self._table_name + ")"

        return table_info_str

    def __eq__(self, other):
        if not isinstance(other, TableInfo):
            return False
        return (self.table_name == other.table_name
                and self.schema_name == other.schema_name
                and self.database_name == other.database_name)


class JoinNode:
    def __init__(self,
                 left: 'TableRef' = None,
                 right: 'TableRef' = None,
                 predicate: AbstractExpression = None,
                 join_type: JoinType = None):
        self.left = left
        self.right = right
        self.predicate = predicate
        self.join_type = join_type

    def __eq__(self, other):
        if not isinstance(other, JoinNode):
            return False
        return (self.left == other.left
                and self.right == other.right
                and self.predicate == other.predicate
                and self.join_type == other.join_type)


class TableRef:
    """
    TableRef: Can be table, subquery, or join
    TODO: port subquery code
    Attributes:
    table_info: expression of table name and database name
    """

    def __init__(self, table_info: TableInfo = None, join: JoinNode = None):
        self._table_info = table_info
        self._join = join
        self._table_ref_type = TableRefType.TABLEATOM

        if join is not None:
            self._table_ref_type = TableRefType.JOIN

    @property
    def table_info(self):
        return self._table_info

    @property
    def join(self):
        return self._join

    @property
    def table_ref_type(self):
        return self._table_ref_type

    def __str__(self):
        if self._table_ref_type is TableRefType.TABLEATOM:
            return str(self._table_info)
        elif self._table_ref_type is TableRefType.JOIN:
            return str(self._join)

    def __eq__(self, other):
        if not isinstance(other, TableRef):
            return False
        return (self.table_info == other.table_info
                and self.join == other.join
                and self.table_ref_type == other.table_ref_type)
