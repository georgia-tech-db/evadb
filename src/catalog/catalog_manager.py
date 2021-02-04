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
from src.catalog.models.base_model import init_db, drop_db
from src.catalog.models.df_column import DataFrameColumn
from src.catalog.models.df_metadata import DataFrameMetadata
from src.catalog.models.udf import UdfMetadata
from src.catalog.models.udf_io import UdfIO
from src.catalog.services.df_column_service import DatasetColumnService
from src.catalog.services.df_service import DatasetService
from src.catalog.services.udf_service import UdfService
from src.catalog.services.udf_io_service import UdfIOService
from src.utils.logging_manager import LoggingLevel
from src.utils.logging_manager import LoggingManager


class CatalogManager(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CatalogManager, cls).__new__(cls)

            cls._instance._bootstrap_catalog()

        return cls._instance

    def __init__(self):
        self._dataset_service = DatasetService()
        self._column_service = DatasetColumnService()
        self._udf_service = UdfService()
        self._udf_io_service = UdfIOService()

    def reset(self):
        """
        This method resets the state of the singleton instance.
        It should drop the catalog table and reinitialize all the member
        variables and services.
        """
        self._shutdown_catalog()
        self._bootstrap_catalog()
        self.__init__()

    def _bootstrap_catalog(self):
        """Bootstraps catalog.

        This method runs all tasks required for using catalog. Currently,
        it includes only one task ie. initializing database. It creates the
        catalog database and tables if they do not exist.

        """
        LoggingManager().log("Bootstrapping catalog", LoggingLevel.INFO)
        init_db()

    def _shutdown_catalog(self):
        """
        This method is responsible for gracefully shutting the
        catalog manager. Currently, it includes dropping the catalog database
        """
        LoggingManager().log("Shutting catalog", LoggingLevel.INFO)
        drop_db()

    def create_metadata(self, name: str, file_url: str,
                        column_list: List[DataFrameColumn],
                        identifier_column='id') -> \
            DataFrameMetadata:
        """Creates metadata object

        Creates a metadata object and column objects and persists them in
        database. Sets the schema field of the metadata object.

        Args:
            name: name of the dataset/video to which this metdata corresponds
            file_url: #todo
            column_list: list of columns
            identifier_column (str):  A unique identifier column for each row

        Returns:
            The persisted DataFrameMetadata object with the id field populated.
        """

        metadata = self._dataset_service.create_dataset(
            name, file_url, identifier_id=identifier_column)
        for column in column_list:
            column.metadata_id = metadata.id
        column_list = self._column_service.create_column(column_list)
        metadata.schema = column_list
        return metadata

    def get_table_bindings(self, database_name: str, table_name: str,
                           column_names: List[str] = None) -> Tuple[int,
                                                                    List[int]]:
        """This method fetches bindings for strings.

        Args:
            database_name: currently not in use
            table_name: the table that is being referred to
            column_names: the column names of the table for which
           bindings are required

        Returns:
            returns metadata_id of table and a list of column ids
        """

        metadata_id = self._dataset_service.dataset_by_name(table_name)
        column_ids = []
        if column_names is not None:
            if not isinstance(column_names, list):
                LoggingManager().log(
                    "CatalogManager::get_table_binding() expected list",
                    LoggingLevel.WARNING)
            column_ids = self._column_service.columns_by_dataset_id_and_names(
                metadata_id,
                column_names)
        return metadata_id, column_ids

    def get_metadata(self, metadata_id: int,
                     col_id_list: List[int] = None) -> DataFrameMetadata:
        """This method returns the metadata object given a metadata_id.

        Arguments:
            metadata_id: metadata id of the table
            col_id_list: optional column ids of the table referred.
                         If none all the columns are required

        Returns:
            metadata object with all the details of video/dataset
        """
        metadata = self._dataset_service.dataset_by_id(metadata_id)
        df_columns = self._column_service.columns_by_id_and_dataset_id(
            metadata_id, col_id_list)
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
        metadata = self._dataset_service.dataset_by_id(table_metadata_id)
        col_types = []
        df_columns = self._column_service.columns_by_id_and_dataset_id(
            metadata.id, col_id_list
        )
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
        df_columns = self._column_service.columns_by_id_and_dataset_id(
            table_metadata_id)
        for col in df_columns:
            col_ids.append(col[0])

        return col_ids

    def create_column_metadata(
            self, column_name: str, data_type: ColumnType,
            dimensions: List[int]):
        """Create a dataframe column object this column.
        This function won't commit this object in the catalog database.
        If you want to commit it into catalog table call create_metadata with
        corresponding table_id

        Arguments:
            column_name {str} -- column name to be created
            data_type {ColumnType} -- type of column created
            dimensions {List[int]} -- dimensions of the column created
        """
        return DataFrameColumn(column_name, data_type,
                               array_dimensions=dimensions)

    def get_dataset_metadata(self, database_name: str, dataset_name: str) -> \
            DataFrameMetadata:
        """
        Returns the Dataset metadata for the given dataset name
        Arguments:
            dataset_name (str): name of the dataset

        Returns:
            DataFrameMetadata
        """

        metadata = self._dataset_service.dataset_object_by_name(
            database_name, dataset_name)
        if metadata is None:
            return None
        # we are forced to set schema every time metadata is fetched
        # ToDo: maybe keep schema as a part of persistent metadata object
        df_columns = self._column_service.columns_by_id_and_dataset_id(
            metadata.id, None)
        metadata.schema = df_columns
        return metadata

    def udf_io(
            self, io_name: str, data_type: ColumnType,
            dimensions: List[int], is_input: bool):
        """Constructs an in memory udf_io object with given info.
        This function won't commit this object in the catalog database.
        If you want to commit it into catalog call create_udf with
        corresponding udf_id and io list

        Arguments:
            name(str): io name to be created
            data_type(ColumnType): type of io created
            dimensions(List[int]):dimensions of the io created
            is_input(bool): whether a input or output, if true it is an input
        """
        return UdfIO(io_name, data_type,
                     array_dimensions=dimensions, is_input=is_input)

    def create_udf(self, name: str, impl_file_path: str,
                   type: str, udf_io_list: List[UdfIO]) -> UdfMetadata:
        """Creates an udf metadata object and udf_io objects and persists them
        in database.

        Arguments:
            name(str): name of the udf to which this metdata corresponds
            impl_file_path(str): implementation path of the udf,
                                 relative to src/udf
            type(str): what kind of udf operator like classification,
                                                        detection etc
            udf_io_list(List[UdfIO]): input/output info of this udf

        Returns:
            The persisted UdfMetadata object with the id field populated.
        """

        metadata = self._udf_service.create_udf(name, impl_file_path, type)
        for udf_io in udf_io_list:
            udf_io.udf_id = metadata.id
        self._udf_io_service.add_udf_io(udf_io_list)
        return metadata

    def get_udf_by_name(self, name: str) -> UdfMetadata:
        """
        Get the UDF information based on name.

        Arguments:
             name (str): name of the UDF

        Returns:
            UdfMetadata object
        """
        return self._udf_service.udf_by_name(name)

    def delete_metadata(self, table_name: str) -> bool:
        """
        This method deletes the table along with its columns from df_metadata
        and df_columns respectively

        Arguments:
           table_name: table name to be deleted.

        Returns:
           True if successfully deleted else False
        """
        metadata_id = self._dataset_service.dataset_by_name(table_name)
        return self._dataset_service.delete_dataset_by_id(metadata_id)

    def delete_udf(self, udf_name: str) -> bool:
        """
        This method drops the udf entry from the catalog

        Arguments:
           udf_name: udf name to be dropped.

        Returns:
           True if successfully deleted else False
        """
        return self._udf_service.delete_udf_by_name(udf_name)

    def get_udf_io_by_name(self, udf_io_name: str) -> UdfIO:
        """Returns the catalog object for the input udfio name

        Args:
            udf_io_name (str): name to query the UDFIO catalog table

        Returns:
            UdfIO: catalog object found
        """
        return self._udf_io_service.udf_io_by_name(udf_io_name)

    def get_udfs_by_type(self, udf_type: str) -> [UdfMetadata]:
        """Returns all the available udfs of input type"""
        return self._udf_service.udfs_by_type(udf_type)
