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

from typing import List, Tuple

from src.catalog.column_type import ColumnType
from src.catalog.models.base_model import init_db
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.models.df_metadata import DataFrameMetadata
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class CatalogManager(object):
    _instance = None
    _catalog = None
    _catalog_dictionary = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CatalogManager, cls).__new__(cls)

            cls._instance.bootstrap_catalog()

        return cls._instance

    def bootstrap_catalog(self):
        """Bootstraps catalog.

        This method runs all tasks required for using catalog. Currently,
        it includes only one task ie. initializing database. It creates the
        catalog database and tables if they do not exist.

        """
        LoggingManager().log("Bootstrapping catalog", LoggingLevel.INFO)
        init_db()

    def create_metadata(self, name: str, file_url: str,
                        column_list: List[DataFrameColumn]) -> \
            DataFrameMetadata:
        """Creates metadata object when called by create executor.

        Creates a metadata object and column objects and persists them in
        database. Sets the schema field of the metadata object.

        Args:
            name: name of the dataset/video to which this metdata corresponds
            file_url: #todo
            column_list: list of columns

        Returns:
            The persisted DataFrameMetadata object with the id field populated.
        """

        metadata = DataFrameMetadata.create(name, file_url)
        for column in column_list:
            column.metadata_id = metadata.id
        column_list = DataFrameColumn.create(column_list)
        metadata.schema = column_list
        return metadata

    def get_table_bindings(self, database_name: str, table_name: str,
                           column_names: List[str]) -> Tuple[int, List[int]]:
        """This method fetches bindings for strings.

        Args:table_metadata_id 
            database_name: currently not in use
            table_name: the table that is being referred to
            column_names: the column names of the table for which
           bindings are required

        Returns:
            returns metadata_id of table and a list of column ids
        """

        metadata_id = DataFrameMetadata.get_id_from_name(table_name)
        column_ids = []
        if column_names is not None:
            if not isinstance(column_names, list):
                LoggingManager().log("CatalogManager::get_table_binding() expected list", LoggingLevel.WARNING) 
            column_ids = DataFrameColumn.get_id_from_metadata_id_and_name_in(
                metadata_id,
                column_names)
        return metadata_id, column_ids

    def get_metadata(self, metadata_id: int,
                     col_id_list: List[int] = None) -> DataFrameMetadata:
        """This method returns the metadata object given a metadata_id,
        when requested by the executor.

        Args:
            metadata_id: metadata id of the table
            col_id_list: optional column ids of the table referred. If none we all the columns are required

        Returns:
            metadata object with all the details of video/dataset
        """
        metadata = DataFrameMetadata.get(metadata_id)
        df_columns = DataFrameColumn.get_by_metadata_id_and_id_in(col_id_list, metadata_id)
        metadata.schema = df_columns
        return metadata

    def get_column_types(self, table_metadata_id: int,
                         col_id_list: List[int]) -> List[ColumnType]:
        """
        This method consumes the input table_id and the input column_id_list
        and
        returns a list of ColumnType for each provided column_id.

        Arguments:
            table_metadata_id {int} -- [metadata_id of the table]
            col_id_list {List[int]} -- [metadata ids of the columns; If list
            = None, return type for all columns in the table]

        Returns:
            List[ColumnType] -- [list of required column type for each input
            column]
        """
        metadata = DataFrameMetadata.get(table_metadata_id)
        col_types = []
        df_columns = DataFrameColumn.get_by_metadata_id_and_id_in(
            col_id_list,
            metadata.id)
        for col in df_columns:
            col_types.append(col.type)

        return col_types

    def get_column_ids(self, table_metadata_id: int) -> List[int]:
        """
        This method returns all the column_ids associated with the given
        table_metadata_id

        Arguments:
            table_metadata_id {int} -- [table metadata id for which columns
            are required]

        Returns:
            List[int] -- [list of columns ids for this table]
        """

        col_ids = []
        df_columns = DataFrameColumn.get_by_metadata_id_and_id_in(
            None,
            table_metadata_id)
        for col in df_columns:
            col_ids.append(col[0])

        return col_ids
