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
from .abstract_expression import AbstractExpression, ExpressionType, \
    ExpressionReturnType


class TupleValueExpression(AbstractExpression):
    def __init__(self, col_name: str = None, table_name: str = None):
        super().__init__(ExpressionType.TUPLE_VALUE,
                         rtype=ExpressionReturnType.INVALID)
        self._col_name = col_name
        self._table_name = table_name
        self._table_metadata_id = None
        self._col_metadata_id = None

    @property
    def table_metadata_id(self) -> int:
        return self._table_metadata_id

    @property
    def col_metadata_id(self) -> int:
        return self._column_metadata_id

    @table_metadata_id.setter
    def table_metadata_id(self, id: int):
        self._table_metadata_id = id

    @col_metadata_id.setter
    def col_metadata_id(self, id: int):
        self._column_metadata_id = id

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def col_name(self) -> str:
        return self._col_name

    # remove this once doen with tuple class
    def evaluate(self, *args):
        tuple1 = None
        if args is None:
            # error Handling
            pass
        tuple1 = args[0]
        return tuple1[(self._col_idx)]
