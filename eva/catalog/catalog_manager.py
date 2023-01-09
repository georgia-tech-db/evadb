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
from pathlib import Path
from typing import List

from eva.catalog.catalog_type import ColumnType, IndexType, TableType
from eva.catalog.catalog_utils import (
    get_image_table_column_definitions,
    get_video_table_column_definitions,
    xform_column_definitions_to_catalog_entries,
)
from eva.catalog.models.base_model import drop_db, init_db
from eva.catalog.models.column_catalog import ColumnCatalogEntry
from eva.catalog.models.index_catalog import IndexCatalogEntry
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.catalog.models.udf_catalog import UdfCatalogEntry
from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.catalog.services.column_catalog_service import ColumnCatalogService
from eva.catalog.services.index_catalog_service import IndexCatalogService
from eva.catalog.services.table_catalog_service import TableCatalogService
from eva.catalog.services.udf_catalog_service import UdfCatalogService
from eva.catalog.services.udf_io_catalog_service import UdfIOCatalogService
from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.parser.create_statement import ColumnDefinition
from eva.parser.table_ref import TableInfo
from eva.parser.types import FileFormatType
from eva.utils.errors import CatalogError
from eva.utils.generic_utils import generate_file_path
from eva.utils.logging_manager import logger


class CatalogManager(object):
    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(CatalogManager, cls).__new__(cls)

            cls._instance._bootstrap_catalog()

        return cls._instance

    def __init__(self):
        self._table_catalog_service: TableCatalogService = TableCatalogService()
        self._column_service: ColumnCatalogService = ColumnCatalogService()
        self._udf_service: UdfCatalogService = UdfCatalogService()
        self._udf_io_service: UdfIOCatalogService = UdfIOCatalogService()
        self._index_service: IndexCatalogService = IndexCatalogService()

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

    "Table catalog services"

    def insert_table_catalog_entry(
        self,
        name: str,
        file_url: str,
        column_list: List[ColumnCatalogEntry],
        identifier_column="id",
        table_type=TableType.VIDEO_DATA,
    ) -> TableCatalogEntry:
        """A new entry is added to the table catalog and persisted in the database.
        The schema field is set before the object is returned."

        Args:
            name: table name
            file_url: #todo
            column_list: list of columns
            identifier_column (str):  A unique identifier column for each row
            table_type (TableType): type of the table, video, images etc
        Returns:
            The persisted TableCatalogEntry object with the id field populated.
        """

        # Append row_id to table column list.
        column_list = [
            ColumnCatalogEntry(name=IDENTIFIER_COLUMN, type=ColumnType.INTEGER)
        ] + column_list

        table_entry = self._table_catalog_service.insert_entry(
            name,
            file_url,
            identifier_column=identifier_column,
            table_type=table_type,
            column_list=column_list,
        )

        return table_entry

    def get_table_catalog_entry(
        self, table_name: str, database_name: str = None
    ) -> TableCatalogEntry:
        """
        Returns the table catalog entry for the given table name
        Arguments:
            table_name (str): name of the table

        Returns:
            TableCatalogEntry
        """

        table_entry = self._table_catalog_service.get_entry_by_name(
            database_name, table_name
        )

        return table_entry

    def delete_table_catalog_entry(self, table_entry: TableCatalogEntry) -> bool:
        """
        This method deletes the table along with its columns from table catalog
        and column catalog respectively

        Arguments:
           table: table catalog entry to remove

        Returns:
           True if successfully deleted else False
        """
        return self._table_catalog_service.delete_entry(table_entry)

    def rename_table_catalog_entry(
        self, curr_table: TableCatalogEntry, new_name: TableInfo
    ):
        return self._table_catalog_service.rename_entry(curr_table, new_name.table_name)

    def check_table_exists(self, table_name: str, database_name: str = None):
        table_entry = self._table_catalog_service.get_entry_by_name(
            database_name, table_name
        )
        if table_entry is None:
            return False
        else:
            return True

    def get_all_table_catalog_entries(self):
        return self._table_catalog_service.get_all_entries()

    "Column catalog services"

    def get_column_catalog_entry(
        self, table_obj: TableCatalogEntry, col_name: str
    ) -> ColumnCatalogEntry:
        col_obj = self._column_service.filter_entry_by_table_id_and_name(
            table_obj.row_id, col_name
        )
        if col_obj:
            return col_obj
        else:
            return None

    def get_column_catalog_entries_by_table(self, table_obj: TableCatalogEntry):
        col_entries = self._column_service.filter_entries_by_table(table_obj)
        return col_entries

    "udf catalog services"

    def insert_udf_catalog_entry(
        self,
        name: str,
        impl_file_path: str,
        type: str,
        udf_io_list: List[UdfIOCatalogEntry],
    ) -> UdfCatalogEntry:
        """Inserts a UDF catalog entry along with UDF_IO entries.
        It persists the entry to the database.

        Arguments:
            name(str): name of the udf
            impl_file_path(str): implementation path of the udf
            type(str): what kind of udf operator like classification,
                                                        detection etc
            udf_io_list(List[UdfIOCatalogEntry]): input/output udf info list

        Returns:
            The persisted UdfCatalogEntry object.
        """

        udf_entry = self._udf_service.insert_entry(name, impl_file_path, type)
        for udf_io in udf_io_list:
            udf_io.udf_id = udf_entry.row_id
        self._udf_io_service.insert_entries(udf_io_list)
        return udf_entry

    def get_udf_catalog_entry_by_name(self, name: str) -> UdfCatalogEntry:
        """
        Get the UDF information based on name.

        Arguments:
             name (str): name of the UDF

        Returns:
            UdfCatalogEntry object
        """
        return self._udf_service.get_entry_by_name(name)

    def delete_udf_catalog_entry_by_name(self, udf_name: str) -> bool:
        return self._udf_service.delete_entry_by_name(udf_name)

    def get_all_udf_catalog_entries(self):
        return self._udf_service.get_all_entries()

    "UdfIO services"

    def get_udf_io_catalog_input_entries(
        self, udf_obj: UdfCatalogEntry
    ) -> List[UdfIOCatalogEntry]:
        return self._udf_io_service.get_input_entries_by_udf_id(udf_obj.row_id)

    def get_udf_io_catalog_output_entries(
        self, udf_obj: UdfCatalogEntry
    ) -> List[UdfIOCatalogEntry]:
        return self._udf_io_service.get_output_entries_by_udf_id(udf_obj.row_id)

    """ Index related services. """

    def insert_index_catalog_entry(
        self,
        name: str,
        save_file_path: str,
        index_type: IndexType,
        feat_column: ColumnCatalogEntry,
        udf_signature: str,
    ) -> IndexCatalogEntry:
        index_catalog_entry = self._index_service.insert_entry(
            name, save_file_path, index_type, feat_column, udf_signature
        )
        return index_catalog_entry

    def get_index_catalog_entry_by_name(self, name: str) -> IndexCatalogEntry:
        return self._index_service.get_entry_by_name(name)

    def get_index_catalog_entry_by_column_and_udf_signature(
        self, column: ColumnCatalogEntry, udf_signature: str
    ):
        return self._index_service.get_entry_by_column_and_udf_signature(
            column, udf_signature
        )

    def drop_index_catalog_entry(self, index_name: str) -> bool:
        return self._index_service.delete_entry_by_name(index_name)

    def get_all_index_catalog_entries(self):
        return self._index_service.get_all_entries()

    """ Utils """

    def create_and_insert_table_catalog_entry(
        self,
        table_info: TableInfo,
        columns: List[ColumnDefinition],
        identifier_column: str = None,
        table_type: TableType = TableType.STRUCTURED_DATA,
    ) -> TableCatalogEntry:
        """Create a valid table catalog tuple and insert into the table

        Args:
            table_info (TableInfo): table info object
            columns (List[ColumnDefinition]): columns definitions of the table
            identifier_column (str, optional): Specify unique columns. Defaults to None.
            table_type (TableType, optional): table type. Defaults to TableType.STRUCTURED_DATA.

        Returns:
            TableCatalogEntry: entry that has been inserted into the table catalog
        """
        table_name = table_info.table_name
        column_catalog_entries = xform_column_definitions_to_catalog_entries(columns)
        file_url = str(generate_file_path(table_name))
        table_catalog_entry = self.insert_table_catalog_entry(
            table_name,
            file_url,
            column_catalog_entries,
            identifier_column=identifier_column,
            table_type=table_type,
        )
        return table_catalog_entry

    def create_and_insert_multimedia_table_catalog_entry(
        self, name: str, format_type: FileFormatType
    ) -> TableCatalogEntry:
        """Create a table catalog entry for the multimedia table.
        Depending on the type of multimedia, the appropriate "create catalog entry" command is called.

        Args:
            name (str):  name of the table catalog entry
            format_type (FileFormatType): media type

        Raises:
            CatalogError: if format_type is not supported

        Returns:
            TableCatalogEntry: newly inserted table catalog entry
        """
        if format_type is FileFormatType.VIDEO:
            columns = get_video_table_column_definitions()
            table_type = TableType.VIDEO_DATA
        elif format_type is FileFormatType.IMAGE:
            columns = get_image_table_column_definitions()
            table_type = TableType.IMAGE_DATA
        else:
            raise CatalogError(f"Format Type {format_type} is not supported")

        return self.create_and_insert_table_catalog_entry(
            TableInfo(name), columns, table_type=table_type
        )

    def get_multimedia_metadata_table_catalog_entry(
        self, input_table: TableCatalogEntry
    ) -> TableCatalogEntry:
        """Get table catalog entry for multimedia metadata table.
        Raise if it does not exists
        Args:
            input_table (TableCatalogEntryEntryEntryEntry): input media table

        Returns:
            TableCatalogEntry: metainfo table entry which is maintained by the system
        """
        # use file_url as the metadata table name
        media_metadata_name = Path(input_table.file_url).stem
        obj = self.get_table_catalog_entry(media_metadata_name)
        if not obj:
            err = f"Table with name {media_metadata_name} does not exist in catalog"
            logger.exception(err)
            raise CatalogError(err)

        return obj

    def create_and_insert_multimedia_metadata_table_catalog_entry(
        self, input_table: TableCatalogEntry
    ) -> TableCatalogEntry:
        """Create and insert table catalog entry for multimedia metadata table.
         This table is used to store all media filenames and related information. In
         order to prevent direct access or modification by users, it should be
         designated as a SYSTEM_STRUCTURED_DATA type.
         **Note**: this table is managed by the storage engine, so it should not be
         called elsewhere.
        Args:
            input_table (TableCatalogEntry): input video table

        Returns:
            TableCatalogEntry: metainfo table entry which is maintained by the system
        """
        # use file_url as the metadata table name
        media_metadata_name = Path(input_table.file_url).stem
        obj = self.get_table_catalog_entry(media_metadata_name)
        if obj:
            err_msg = f"Table with name {media_metadata_name} already exists"
            logger.exception(err_msg)
            raise CatalogError(err_msg)

        columns = [ColumnDefinition("file_url", ColumnType.TEXT, None, None)]
        obj = self.create_and_insert_table_catalog_entry(
            TableInfo(media_metadata_name),
            columns,
            identifier_column=columns[0].name,
            table_type=TableType.SYSTEM_STRUCTURED_DATA,
        )
        return obj
