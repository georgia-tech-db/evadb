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
from typing import Dict, List, Tuple, Union

from eva.binder.binder_utils import BinderError
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.models.udf_io import UdfIO
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.utils.logging_manager import logger

CatalogColumnType = Union[DataFrameColumn, UdfIO]


class StatementBinderContext:
    """
    `_table_alias_map`: Maintains a mapping from table_alias to
    corresponding catalog table object
    `_derived_table_alias_map`:
    Maintains a mapping from derived table alias (subquery, FunctionExpression)
    to the corresponding projected columns.
    For example, in the follwoing queries: Select * FROM (SELECT id1, id2
    FROM table) AS A;
         A: [id1, id2]
    Select * FROM video LATERAL JOIN func;
         func: [func.col1, func.col2]
    """

    def __init__(self):
        self._table_alias_map: Dict[str, DataFrameMetadata] = dict()
        self._derived_table_alias_map: Dict[str, List[CatalogColumnType]] = dict()
        self._catalog = CatalogManager()

    def _check_duplicate_alias(self, alias: str):
        """
        Sanity check: no duplicate alias in table and derived_table
        Arguments:
            alias (str): name of the alias

        Exception:
            Raise exception if found duplication
        """
        if alias in self._derived_table_alias_map or alias in self._table_alias_map:
            err_msg = f"Found duplicate alias {alias}"
            logger.error(err_msg)
            raise BinderError(err_msg)

    def add_table_alias(self, alias: str, table_name: str):
        """
        Add a alias -> table_name mapping
        Arguments:
            alias (str): name of alias
            table_name (str): name of the table
        """
        self._check_duplicate_alias(alias)
        table_obj = self._catalog.get_dataset_metadata(None, table_name)
        self._table_alias_map[alias] = table_obj

    def add_derived_table_alias(
        self,
        alias: str,
        target_list: List[Union[TupleValueExpression, FunctionExpression, UdfIO]],
    ):
        """
        Add a alias -> derived table column mapping
        Arguments:
            alias (str): name of alias
            target_list: list of Tuplevalue Expression or FunctionExpression or UdfIO
        """
        self._check_duplicate_alias(alias)
        col_list = []
        for expr in target_list:
            if isinstance(expr, FunctionExpression):
                col_list.extend(expr.output_objs)
            elif isinstance(expr, TupleValueExpression):
                col_list.append(expr.col_object)
            else:
                col_list.append(expr)

        self._derived_table_alias_map[alias] = col_list

    def get_binded_column(
        self, col_name: str, alias: str = None
    ) -> Tuple[str, CatalogColumnType]:
        """
        Find the binded column object
        Arguments:
            col_name (str): columna name
            alias (str): alias name

        Returns:
            A tuple of alias and column object
        """

        def raise_error():
            err_msg = f"Found invalid column {col_name}"
            logger.error(err_msg)
            raise BinderError(err_msg)

        if not alias:
            alias, col_obj = self._search_all_alias_maps(col_name)
        else:
            # serach in all alias maps
            col_obj = self._check_table_alias_map(alias, col_name)
            if not col_obj:
                col_obj = self._check_derived_table_alias_map(alias, col_name)

        if col_obj:
            return alias, col_obj

        raise_error()

    def _check_table_alias_map(self, alias, col_name) -> DataFrameColumn:
        """
        Find the column object in table alias map
        Arguments:
            col_name (str): columna name
            alias (str): alias name

        Returns:
            column object
        """
        table_obj = self._table_alias_map.get(alias, None)
        if table_obj:
            return self._catalog.get_column_object(table_obj, col_name)

    def _check_derived_table_alias_map(self, alias, col_name) -> CatalogColumnType:
        """
        Find the column object in derived table alias map
        Arguments:
            col_name (str): column name
            alias (str): alias name

        Returns:
            column object
        """
        col_objs = self._derived_table_alias_map.get(alias, None)
        if col_objs:
            for obj in col_objs:
                if obj.name.lower() == col_name:
                    return obj

    def _get_all_alias_and_col_name(self) -> List[Tuple[str, str]]:
        """
        Return all alias and column objects mapping in the current context
        Returns:
            a list of tuple of alias name, column name
        """
        alias_cols = []
        for alias, table_obj in self._table_alias_map.items():
            alias_cols += list([(alias, col.name) for col in table_obj.columns])
        for alias, dtable_obj in self._derived_table_alias_map.items():
            alias_cols += list([(alias, col.name) for col in dtable_obj])
        return alias_cols

    def _search_all_alias_maps(self, col_name: str) -> Tuple[str, CatalogColumnType]:
        """
        Search the alias and column object using column name
        Arguments:
            col_name (str): column name

        Returns:
            A tuple of alias and column object.
        """
        num_alias_matches = 0
        alias_match = None
        match_obj = None
        for alias in self._table_alias_map:
            col_obj = self._check_table_alias_map(alias, col_name)
            if col_obj:
                match_obj = col_obj
                num_alias_matches += 1
                alias_match = alias

        for alias in self._derived_table_alias_map:
            col_obj = self._check_derived_table_alias_map(alias, col_name)
            if col_obj:
                match_obj = col_obj
                num_alias_matches += 1
                alias_match = alias

        if num_alias_matches > 1:
            err_msg = "Ambiguous Column name {col_name}"
            logger.error(err_msg)
            raise BinderError(err_msg)

        return alias_match, match_obj
