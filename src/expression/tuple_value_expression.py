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
from src.catalog.models.df_column import DataFrameColumn
from src.models.storage.batch import Batch
from .abstract_expression import AbstractExpression, ExpressionType, \
    ExpressionReturnType
from src.models.server.metrics import timer


class TupleValueExpression(AbstractExpression):
    def __init__(self, col_name: str = None, table_name: str = None,
                 col_idx: int = -1, col_object: DataFrameColumn = None):
        super().__init__(ExpressionType.TUPLE_VALUE,
                         rtype=ExpressionReturnType.INVALID)
        self._col_name = col_name
        self._table_name = table_name
        self._table_metadata_id = None
        self._col_metadata_id = None
        self._col_idx = col_idx
        self._col_object = col_object

    @property
    def table_metadata_id(self) -> int:
        return self._table_metadata_id

    @property
    def col_metadata_id(self) -> int:
        return self._col_metadata_id

    @table_metadata_id.setter
    def table_metadata_id(self, id: int):
        self._table_metadata_id = id

    @col_metadata_id.setter
    def col_metadata_id(self, id: int):
        self._col_metadata_id = id

    @property
    def table_name(self) -> str:
        return self._table_name

    @table_name.setter
    def table_name(self, name: str):
        self._table_name = name

    @property
    def col_name(self) -> str:
        return self._col_name

    @property
    def col_object(self) -> DataFrameColumn:
        return self._col_object

    @col_object.setter
    def col_object(self, value: DataFrameColumn):
        self._col_object = value

    @timer
    def evaluate(self, batch: Batch, *args):
        if args is None:
            # error Handling
            pass

        return batch.project([self.col_name])

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, TupleValueExpression):
            return False
        return (is_subtree_equal and self.table_name == other.table_name
                and self.table_metadata_id == other.table_metadata_id
                and self.col_name == other.col_name
                and self.col_metadata_id == other.col_metadata_id
                and self.col_object == other.col_object
                and self._col_idx == other._col_idx)
