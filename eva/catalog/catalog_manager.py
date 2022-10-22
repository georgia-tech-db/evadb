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
from typing import List

from eva.catalog.column_type import ColumnType, NdArrayType
from eva.catalog.models.base_model import drop_db, init_db
from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.models.udf import UdfMetadata
from eva.catalog.models.udf_io import UdfIO
from eva.catalog.services.df_column_service import DatasetColumnService
from eva.catalog.services.df_service import DatasetService
from eva.catalog.services.udf_io_service import UdfIOService
from eva.catalog.services.udf_service import UdfService
from eva.parser.create_statement import ColConstraintInfo
from eva.parser.table_ref import TableInfo
from eva.utils.logging_manager import logger


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
        logger.info("Bootstrapping catalog")
        init_db()

    def _shutdown_catalog(self):
        """
        This method is responsible for gracefully shutting the
        catalog manager. Currently, it includes dropping the catalog database
        """
        logger.info("Shutting catalog")
        drop_db()

    def create_metadata(
        self,
        name: str,
        file_url: str,
        column_list: List[DataFrameColumn],
        identifier_column="id",
        is_video=False,
    ) -> DataFrameMetadata:
        """Creates metadata object

        Creates a metadata object and column objects and persists them in
        database. Sets the schema field of the metadata object.

        Args:
            name: name of the dataset/video to which this metdata corresponds
            file_url: #todo
            column_list: list of columns
            identifier_column (str):  A unique identifier column for each row
            is_video (bool): True if the table is a video
        Returns:
            The persisted DataFrameMetadata object with the id field populated.
        """

        metadata = self._dataset_service.create_dataset(
            name, file_url, identifier_id=identifier_column, is_video=is_video
        )
        for column in column_list:
            column.metadata_id = metadata.id
        column_list = self._column_service.create_column(column_list)
        metadata.schema = column_list
        return metadata

    def create_column_metadata(
        self,
        column_name: str,
        data_type: ColumnType,
        array_type: NdArrayType,
        dimensions: List[int],
        cci: ColConstraintInfo,
    ) -> DataFrameColumn:
        """Create a dataframe column object this column.
        This function won't commit this object in the catalog database.
        If you want to commit it into catalog table call create_metadata with
        corresponding table_id

        Arguments:
            column_name {str} -- column name to be created
            data_type {ColumnType} -- type of column created
            array_type {NdArrayType} -- type of ndarray
            dimensions {List[int]} -- dimensions of the column created
        """
        return DataFrameColumn(
            column_name,
            data_type,
            array_type=array_type,
            array_dimensions=dimensions,
            is_nullable=cci.nullable,
        )

    def get_dataset_metadata(
        self, database_name: str, dataset_name: str
    ) -> DataFrameMetadata:
        """
        Returns the Dataset metadata for the given dataset name
        Arguments:
            dataset_name (str): name of the dataset

        Returns:
            DataFrameMetadata
        """

        metadata = self._dataset_service.dataset_object_by_name(
            database_name, dataset_name
        )
        if metadata is None:
            return None
        # we are forced to set schema every time metadata is fetched
        # ToDo: maybe keep schema as a part of persistent metadata object
        df_columns = self._column_service.columns_by_id_and_dataset_id(
            metadata.id, None
        )
        metadata.schema = df_columns
        return metadata

    def get_column_object(
        self, table_obj: DataFrameMetadata, col_name: str
    ) -> DataFrameColumn:
        col_objs = self._column_service.columns_by_dataset_id_and_names(
            table_obj.id, column_names=[col_name]
        )
        if col_objs:
            return col_objs[0]
        else:
            return None

    def get_all_column_objects(self, table_obj: DataFrameMetadata):
        col_objs = self._column_service.get_dataset_columns(table_obj)
        return col_objs

    def udf_io(
        self,
        io_name: str,
        data_type: ColumnType,
        array_type: NdArrayType,
        dimensions: List[int],
        is_input: bool,
    ):
        """Constructs an in memory udf_io object with given info.
        This function won't commit this object in the catalog database.
        If you want to commit it into catalog call create_udf with
        corresponding udf_id and io list

        Arguments:
            name(str): io name to be created
            data_type(ColumnType): type of io created
            array_type(NdArrayType): type of array content
            dimensions(List[int]):dimensions of the io created
            is_input(bool): whether a input or output, if true it is an input
        """
        return UdfIO(
            io_name,
            data_type,
            array_type=array_type,
            array_dimensions=dimensions,
            is_input=is_input,
        )

    def create_udf(
        self,
        name: str,
        impl_file_path: str,
        type: str,
        udf_io_list: List[UdfIO],
    ) -> UdfMetadata:
        """Creates an udf metadata object and udf_io objects and persists them
        in database.

        Arguments:
            name(str): name of the udf to which this metdata corresponds
            impl_file_path(str): implementation path of the udf,
                                 relative to eva/udf
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

    def get_udf_inputs(self, udf_obj: UdfMetadata) -> List[UdfIO]:
        if not isinstance(udf_obj, UdfMetadata):
            raise ValueError(
                """Expected UdfMetadata object, got
                             {}""".format(
                    type(udf_obj)
                )
            )
        return self._udf_io_service.get_inputs_by_udf_id(udf_obj.id)

    def get_udf_outputs(self, udf_obj: UdfMetadata) -> List[UdfIO]:
        if not isinstance(udf_obj, UdfMetadata):
            raise ValueError(
                """Expected UdfMetadata object, got
                             {}""".format(
                    type(udf_obj)
                )
            )
        return self._udf_io_service.get_outputs_by_udf_id(udf_obj.id)

    def drop_dataset_metadata(self, database_name: str, table_name: str) -> bool:
        """
        This method deletes the table along with its columns from df_metadata
        and df_columns respectively

        Arguments:
           table_name: table name to be deleted.

        Returns:
           True if successfully deleted else False
        """
        return self._dataset_service.drop_dataset_by_name(database_name, table_name)

    def drop_udf(self, udf_name: str) -> bool:
        """
        This method drops the udf entry and corresponding udf_io
        from the catalog

        Arguments:
           udf_name: udf name to be dropped.

        Returns:
           True if successfully deleted else False
        """
        return self._udf_service.drop_udf_by_name(udf_name)

    def rename_table(self, new_name: TableInfo, curr_table: TableInfo):
        return self._dataset_service.rename_dataset_by_name(
            new_name.table_name,
            curr_table.database_name,
            curr_table.table_name,
        )

    def check_table_exists(self, database_name: str, table_name: str):
        metadata = self._dataset_service.dataset_object_by_name(
            database_name, table_name
        )
        if metadata is None:
            return False
        else:
            return True

    def get_all_udf_entries(self):
        return self._udf_service.get_all_udfs()
