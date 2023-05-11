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
from eva.catalog.models.column_catalog import ColumnCatalogEntry
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.utils.logging_manager import logger

CatalogColumnType = Union[ColumnCatalogEntry, UdfIOCatalogEntry]


class StatementBinderContext:
    """
    This context is used to store information that is useful during the process of binding a statement (such as a SELECT statement) to the catalog. It stores the following information:

    Args:
        `_table_alias_map`: Maintains a mapping from table_alias to corresponding
        catalog table entry
        `_derived_table_alias_map`: Maintains a mapping from derived table aliases,
        such as subqueries or function expressions, to column alias maps for all the
        corresponding projected columns. For example, in the following queries, the
        `_derived_table_alias_map` attribute would contain:

        `Select * FROM (SELECT id1, id2 FROM table) AS A` :
            `{A: {id1: table.col1, id2: table.col2}}`
        `Select * FROM video LATERAL JOIN func AS T(a, b)` :
            `{T: {a: func.obj1, b:func.obj2}}`
    """

    def __init__(self):
        self._table_alias_map: Dict[str, TableCatalogEntry] = dict()
        self._derived_table_alias_map: Dict[str, Dict[str, CatalogColumnType]] = dict()
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
        table_obj = self._catalog.get_table_catalog_entry(table_name)
        self._table_alias_map[alias] = table_obj

    def add_derived_table_alias(
        self,
        alias: str,
        target_list: List[
            Union[TupleValueExpression, FunctionExpression, UdfIOCatalogEntry]
        ],
    ):
        """
        Add a alias -> derived table column mapping
        Arguments:
            alias (str): name of alias
            target_list: list of Tuplevalue Expression or FunctionExpression or UdfIOCatalogEntry
        """
        self._check_duplicate_alias(alias)
        col_alias_map = {}
        for expr in target_list:
            if isinstance(expr, FunctionExpression):
                for obj in expr.output_objs:
                    col_alias_map[obj.name] = obj
            elif isinstance(expr, TupleValueExpression):
                col_alias_map[expr.col_name] = expr.col_object
            else:
                continue

        self._derived_table_alias_map[alias] = col_alias_map

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

    def _check_table_alias_map(self, alias, col_name) -> ColumnCatalogEntry:
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
            return self._catalog.get_column_catalog_entry(table_obj, col_name)

    def _check_derived_table_alias_map(self, alias, col_name) -> CatalogColumnType:
        """
        Find the column object in derived table alias map
        Arguments:
            col_name (str): column name
            alias (str): alias name

        Returns:
            column object
        """
        col_objs_map = self._derived_table_alias_map.get(alias, None)
        if col_objs_map is None:
            return None

        for name, obj in col_objs_map.items():
            if name == col_name:
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
        for alias, col_objs_map in self._derived_table_alias_map.items():
            alias_cols += list([(alias, col_name) for col_name in col_objs_map])
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
