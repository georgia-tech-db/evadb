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
from eva.catalog.models.df_column import DataFrameColumn
from eva.models.storage.batch import Batch

from .abstract_expression import (
    AbstractExpression,
    ExpressionReturnType,
    ExpressionType,
)


class TupleValueExpression(AbstractExpression):
    def __init__(
        self,
        col_name: str = None,
        table_alias: str = None,
        col_idx: int = -1,
        col_object: DataFrameColumn = None,
        col_alias=None,
    ):
        super().__init__(ExpressionType.TUPLE_VALUE, rtype=ExpressionReturnType.INVALID)
        self._col_name = col_name
        self._table_alias = table_alias
        self._table_metadata_id = None
        self._col_idx = col_idx
        self._col_object = col_object
        self._col_alias = col_alias

    @property
    def table_metadata_id(self) -> int:
        return self._table_metadata_id

    @table_metadata_id.setter
    def table_metadata_id(self, id: int):
        self._table_metadata_id = id

    @property
    def table_alias(self) -> str:
        return self._table_alias

    @table_alias.setter
    def table_alias(self, name: str):
        self._table_alias = name

    @property
    def col_name(self) -> str:
        return self._col_name

    @property
    def col_object(self) -> DataFrameColumn:
        return self._col_object

    @col_object.setter
    def col_object(self, value: DataFrameColumn):
        self._col_object = value

    @property
    def col_alias(self) -> str:
        return self._col_alias

    @col_alias.setter
    def col_alias(self, value: str):
        self._col_alias = value

    def evaluate(self, batch: Batch, *args, **kwargs):
        if "mask" in kwargs:
            batch = batch[kwargs["mask"]]
        return batch.project([self.col_alias])

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, TupleValueExpression):
            return False
        return (
            is_subtree_equal
            and self.table_alias == other.table_alias
            and self.table_metadata_id == other.table_metadata_id
            and self.col_name == other.col_name
            and self.col_alias == other.col_alias
            and self.col_object == other.col_object
            and self._col_idx == other._col_idx
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_alias,
                self.table_metadata_id,
                self.col_name,
                self.col_alias,
                self.col_object,
                self._col_idx,
            )
        )
