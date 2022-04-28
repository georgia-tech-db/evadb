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

from typing import Dict, List, Tuple, Union

from matplotlib.pyplot import table
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.models.df_column import DataFrameColumn

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.models.udf import UdfMetadata
from eva.catalog.models.udf_io import UdfIO
from eva.utils.logging_manager import LoggingLevel, LoggingManager


class StatementBinderContext:
    def __init__(self):
        self._table_alias_map: Dict[str, DataFrameMetadata] = dict()
        self._func_alias_map: Dict[str, UdfMetadata] = dict()
        self._derived_table_alias_map: Dict[str, List[DataFrameColumn]] = dict()
        self._catalog = CatalogManager()
    
    def _check_duplicate_alias(self, alias):
        if alias in self._derived_table_alias_map or alias in self._func_alias_map or alias in self._table_alias_map: 
            raise RuntimeError('Found duplicate alias {}'.format(alias))

    def add_table_alias(self, alias: str, table_name: str):
        self._check_duplicate_alias(alias)
        table_obj = self._catalog.get_dataset_metadata(None, table_name)
        self._table_alias_map[alias] = table_obj
    
    def add_function_alias(self, alias: str, func_name: str):
        self._check_duplicate_alias(alias)
        func_obj = self._catalog.get_udf_by_name(func_name)
        self._func_alias_map[alias] = func_obj
    
    def add_derived_table_alias(self, alias: str, target_list: List[DataFrameColumn]):
        self._check_duplicate_alias(alias)
        self._derived_table_alias_map[alias] = target_list
            
    def get_binded_column(self, 
                          col_name: str, 
                          alias: str = None) -> Tuple[str, Union[DataFrameColumn, UdfIO]]:
        def raise_error():
            err_msg = 'Invalid column = {}'.format(col_name)
            LoggingManager().log(err_msg, LoggingLevel.ERROR)
            raise RuntimeError(err_msg)
        
        if not alias:
            alias, col_obj = self._search_all_alias_maps(col_name)
        else:
            # serach in all alias maps
            col_obj = self._check_table_alias_map(alias, col_name)
            if not col_obj:
                col_obj = self._check_derived_table_alias_map(alias, col_name)
            if not col_obj:
                col_obj = self._check_func_alias_map(alias, col_name)

        if col_obj:
            return alias, col_obj
        
        raise_error()
    
    def _check_table_alias_map(self, alias, col_name) -> DataFrameColumn:
        table_obj = self._table_alias_map.get(alias, None)
        if table_obj:
            return self._catalog.get_column_object(table_obj, col_name)
    
    def _check_derived_table_alias_map(self, alias, col_name) ->DataFrameColumn:
        col_objs = self._derived_table_alias_map.get(alias, None)
        if col_objs:
            for obj in col_objs:
                if obj.col_name.lower() == col_name:
                    return obj

    def _check_func_alias_map(self, alias, col_name) -> UdfIO:
        func_obj = self._func_alias_map.get(alias, None)
        if func_obj:
            return self._catalog.get_udf_io_by_name(func_obj, col_name)

    def _search_all_alias_maps(self, 
                                 col_name: str) -> Tuple[str, Union[DataFrameColumn, 
                                                               UdfIO]]:
        num_alias_matches = 0
        alias_match = None
        match_obj = None
        for alias in self._table_alias_map:
            col_obj = self._check_table_alias_map(alias, col_name)
            if col_obj:
                match_obj = col_obj
                num_alias_matches += 1 
                alias_match =  alias 

        for alias in self._derived_table_alias_map:
            col_obj = self._check_derived_table_alias_map(alias, col_name)
            if col_obj:
                match_obj = col_obj
                num_alias_matches += 1 
                alias_match =  alias 

        for alias in self._func_alias_map.keys():
            col_obj = self._check_func_alias_map(alias, col_name)
            if col_obj:
                match_obj = col_obj
                num_alias_matches += 1 
                alias_match =  alias 

        if num_alias_matches > 1:
            err_msg = 'Ambiguous Column name = {}'.format(col_name)
            LoggingManager().log(err_msg, LoggingLevel.ERROR)  
            raise RuntimeError(err_msg)  
        
        return alias_match, match_obj 