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

from typing import List
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.column_type import ColumnType, NdArrayType
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.parser.create_statement import ColConstraintInfo, ColumnDefinition
from eva.parser.table_ref import TableInfo, TableRef
from eva.utils.generic_utils import generate_file_path
from eva.binder.statement_binder_context import StatementBinderContext
from eva.expression.abstract_expression import AbstractExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.utils.logging_manager import logger


def create_video_metadata(name: str) -> DataFrameMetadata:
    """Create video metadata object.
        We have predefined columns for such a object
        id:  the frame id
        data: the frame data

    Arguments:
        name (str): name of the metadata to be added to the catalog

    Returns:
        DataFrameMetadata:  corresponding metadata for the input table info
    """
    catalog = CatalogManager()
    columns = [ColumnDefinition('id', ColumnType.INTEGER, None,
                                [], ColConstraintInfo(unique=True))]
    # the ndarray dimensions are set as None. We need to fix this as we
    # cannot assume. Either ask the user to provide this with load or
    # we infer this from the provided video.
    columns.append(
        ColumnDefinition(
            'data', ColumnType.NDARRAY, NdArrayType.UINT8, [None, None, None]
        )
    )
    col_metadata = create_column_metadata(columns)
    uri = str(generate_file_path(name))
    metadata = catalog.create_metadata(
        name, uri, col_metadata, identifier_column='id', is_video=True)
    return metadata


def create_table_metadata(table_ref: TableRef,
                          columns: List[ColumnDefinition])\
        -> DataFrameMetadata:
    table_name = table_ref.table.table_name
    column_metadata_list = create_column_metadata(columns)
    file_url = str(generate_file_path(table_name))
    metadata = CatalogManager().create_metadata(table_name,
                                                file_url,
                                                column_metadata_list)
    return metadata


def create_column_metadata(col_list: List[ColumnDefinition]):
    """Create column metadata for the input parsed column list. This function
    will not commit the provided column into catalog table.
    Will only return in memory list of ColumnDataframe objects

    Arguments:
        col_list {List[ColumnDefinition]} -- parsed col list to be created
    """
    if isinstance(col_list, ColumnDefinition):
        col_list = [col_list]

    result_list = []
    for col in col_list:
        if col is None:
            logger.error(
                "Empty column while creating column metadata")
            result_list.append(col)
        result_list.append(
            CatalogManager().create_column_metadata(
                col.name, col.type, col.array_type, col.dimension
            )
        )

    return result_list


def bind_table_info(table_info: TableInfo) -> DataFrameMetadata:
    """
    Uses catalog to bind the dataset information for given video string.

    Arguments:
         video_info (TableInfo): video information obtained in SQL query

    Returns:
        DataFrameMetadata  -  corresponding metadata for the input table info
    """
    catalog = CatalogManager()
    obj = catalog.get_dataset_metadata(table_info.database_name,
                                       table_info.table_name)
    if obj:
        table_info.table_obj = obj
    else:
        error = '{} does not exists. Create the table using \
                        CREATE TABLE.'.format(table_info.table_name)
        logger.error(error)
        raise RuntimeError(error)


def handle_if_not_exists(table_ref: TableRef, if_not_exist=False):
    if CatalogManager().check_table_exists(table_ref.table.database_name,
                                           table_ref.table.table_name):
        err_msg = 'Table: {} already exsits'.format(table_ref)
        if if_not_exist:
            logger.warn(err_msg)
            return True
        else:
            logger.error(err_msg)
            raise RuntimeError(err_msg)
    else:
        return False


def extend_star_in_target_list(
    alias: str,
    binder_context: StatementBinderContext
) -> List[AbstractExpression]:
    col_names = binder_context._search_all_col_name(alias)
    target_list = list(
        [TupleValueExpression(col_name=col_name, table_alias=alias) 
            for col_name in col_names]
    )
    return target_list
