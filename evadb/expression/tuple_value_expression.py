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
from typing import Union

from evadb.catalog.models.column_catalog import ColumnCatalogEntry
from evadb.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from evadb.models.storage.batch import Batch

from .abstract_expression import (
    AbstractExpression,
    ExpressionReturnType,
    ExpressionType,
)


class TupleValueExpression(AbstractExpression):
    def __init__(
        self,
        name: str = None,
        table_alias: str = None,
        col_object: Union[ColumnCatalogEntry, UdfIOCatalogEntry] = None,
        col_alias=None,
    ):
        super().__init__(ExpressionType.TUPLE_VALUE, rtype=ExpressionReturnType.INVALID)
        self._name = name
        self._table_alias = table_alias
        self._col_object = col_object
        self._col_alias = col_alias

    @property
    def table_alias(self) -> str:
        return self._table_alias

    @table_alias.setter
    def table_alias(self, table_alias):
        self._table_alias = table_alias

    @property
    def name(self) -> str:
        return self._name

    @property
    def col_object(self) -> Union[ColumnCatalogEntry, UdfIOCatalogEntry]:
        return self._col_object

    @col_object.setter
    def col_object(self, value: Union[ColumnCatalogEntry, UdfIOCatalogEntry]):
        self._col_object = value

    @property
    def col_alias(self) -> str:
        return self._col_alias

    @col_alias.setter
    def col_alias(self, value: str):
        self._col_alias = value

    def evaluate(self, batch: Batch, *args, **kwargs):
        return batch.project([self.col_alias])

    def signature(self):
        """It constructs the signature of the tuple value expression.
        It assumes the col_object attribute is populated by the binder with the catalog
        entries. For a standard column in the table, it returns `table_name.col_name`,
        and for UDF output columns it returns `udf_name.col_name`
        Raises:
            ValueError: If the col_object is not a `Union[ColumnCatalogEntry, UdfIOCatalogEntry]`. This can occur if the expression has not been bound using the binder.
        Returns:
            str: signature string
        """
        assert isinstance(self.col_object, ColumnCatalogEntry) or isinstance(
            self.col_object, UdfIOCatalogEntry
        ), f"Unsupported type of self.col_object {type(self.col_object)}, expected ColumnCatalogEntry or UdfIOCatalogEntry"

        col_name = self.col_object.name
        row_id = self.col_object.row_id
        if isinstance(self.col_object, ColumnCatalogEntry):
            return f"{self.col_object.table_name}.{col_name}[{row_id}]"
        elif isinstance(self.col_object, UdfIOCatalogEntry):
            return f"{self.col_object.udf_name}.{col_name}[{row_id}]"

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, TupleValueExpression):
            return False
        return (
            is_subtree_equal
            and self.table_alias == other.table_alias
            and self.name == other.name
            and self.col_alias == other.col_alias
            and self.col_object == other.col_object
        )

    def __str__(self) -> str:
        expr_str = ""
        if self.table_alias:
            expr_str += f"{str(self.table_alias)}."
        if self.name:
            expr_str += f"{str(self.name)}"
        if self.col_alias:
            expr_str += f" AS {str(self.col_alias)}"
        expr_str += ""
        return expr_str

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.table_alias,
                self.name,
                self.col_alias,
                self.col_object,
            )
        )
