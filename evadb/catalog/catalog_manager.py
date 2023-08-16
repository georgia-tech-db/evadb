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
import shutil
from pathlib import Path
from typing import List

from evadb.catalog.catalog_type import (
    ColumnType,
    TableType,
    VectorStoreType,
    VideoColumnName,
)
from evadb.catalog.catalog_utils import (
    cleanup_storage,
    construct_udf_cache_catalog_entry,
    get_document_table_column_definitions,
    get_image_table_column_definitions,
    get_pdf_table_column_definitions,
    get_video_table_column_definitions,
    xform_column_definitions_to_catalog_entries,
)
from evadb.catalog.models.utils import (
    ColumnCatalogEntry,
    DatabaseCatalogEntry,
    IndexCatalogEntry,
    TableCatalogEntry,
    UdfCacheCatalogEntry,
    UdfCatalogEntry,
    UdfCostCatalogEntry,
    UdfIOCatalogEntry,
    UdfMetadataCatalogEntry,
    drop_all_tables_except_catalog,
    init_db,
    truncate_catalog_tables,
)
from evadb.catalog.services.column_catalog_service import ColumnCatalogService
from evadb.catalog.services.database_catalog_service import DatabaseCatalogService
from evadb.catalog.services.index_catalog_service import IndexCatalogService
from evadb.catalog.services.table_catalog_service import TableCatalogService
from evadb.catalog.services.udf_cache_catalog_service import UdfCacheCatalogService
from evadb.catalog.services.udf_catalog_service import UdfCatalogService
from evadb.catalog.services.udf_cost_catalog_service import UdfCostCatalogService
from evadb.catalog.services.udf_io_catalog_service import UdfIOCatalogService
from evadb.catalog.services.udf_metadata_catalog_service import (
    UdfMetadataCatalogService,
)
from evadb.catalog.sql_config import IDENTIFIER_COLUMN, SQLConfig
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.expression.function_expression import FunctionExpression
from evadb.parser.create_statement import ColumnDefinition
from evadb.parser.table_ref import TableInfo
from evadb.parser.types import FileFormatType
from evadb.utils.generic_utils import generate_file_path, get_file_checksum
from evadb.utils.logging_manager import logger


class CatalogManager(object):
    def __init__(self, db_uri: str, config: ConfigurationManager):
        self._db_uri = db_uri
        self._sql_config = SQLConfig(db_uri)
        self._config = config
        self._bootstrap_catalog()
        self._db_catalog_service = DatabaseCatalogService(self._sql_config.session)
        self._table_catalog_service = TableCatalogService(self._sql_config.session)
        self._column_service = ColumnCatalogService(self._sql_config.session)
        self._udf_service = UdfCatalogService(self._sql_config.session)
        self._udf_cost_catalog_service = UdfCostCatalogService(self._sql_config.session)
        self._udf_io_service = UdfIOCatalogService(self._sql_config.session)
        self._udf_metadata_service = UdfMetadataCatalogService(self._sql_config.session)
        self._index_service = IndexCatalogService(self._sql_config.session)
        self._udf_cache_service = UdfCacheCatalogService(self._sql_config.session)

    @property
    def sql_config(self):
        return self._sql_config

    def reset(self):
        """
        This method resets the state of the singleton instance.
        It should clear the contents of the catalog tables and any storage data
        Used by testcases to reset the db state before
        """
        self._clear_catalog_contents()

    def close(self):
        """
        This method closes all the connections
        """
        if self.sql_config is not None:
            sqlalchemy_engine = self.sql_config.engine
            sqlalchemy_engine.dispose()

    def _bootstrap_catalog(self):
        """Bootstraps catalog.
        This method runs all tasks required for using catalog. Currently,
        it includes only one task ie. initializing database. It creates the
        catalog database and tables if they do not exist.
        """
        logger.info("Bootstrapping catalog")
        init_db(self._sql_config.engine)

    def _clear_catalog_contents(self):
        """
        This method is responsible for clearing the contents of the
        catalog. It clears the tuples in the catalog tables, indexes, and cached data.
        """
        logger.info("Clearing catalog")
        # drop tables which are not part of catalog
        drop_all_tables_except_catalog(self._sql_config.engine)
        # truncate the catalog tables
        truncate_catalog_tables(self._sql_config.engine)
        # clean up the dataset, index, and cache directories
        cleanup_storage(self._config)

    "Database catalog services"

    def insert_database_catalog_entry(self, name: str, engine: str, params: dict):
        """A new entry is persisted in the database catalog."

        Args:
            name: database name
            engine: engine name
            params: required params as a dictionary for the database
        """
        self._db_catalog_service.insert_entry(name, engine, params)

    def get_database_catalog_entry(self, database_name: str) -> DatabaseCatalogEntry:
        """
        Returns the database catalog entry for the given database_name
        Arguments:
            database_name (str): name of the database

        Returns:
            DatabaseCatalogEntry
        """

        table_entry = self._db_catalog_service.get_entry_by_name(database_name)

        return table_entry

    def delete_database_catalog_entry(
        self, database_entry: DatabaseCatalogEntry
    ) -> bool:
        """
        This method deletes the database from  catalog.

        Arguments:
           database_entry: database catalog entry to remove

        Returns:
           True if successfully deleted else False
        """
        # todo: do we need to remove also the associated tables etc or that will be
        # taken care by the underlying db
        return self._db_catalog_service.delete_entry(database_entry)

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
            # return a dummy column catalog entry for audio, even though it does not defined for videos
            if col_name == VideoColumnName.audio:
                return ColumnCatalogEntry(
                    col_name,
                    ColumnType.NDARRAY,
                    table_id=table_obj.row_id,
                    table_name=table_obj.name,
                )
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
        udf_metadata_list: List[UdfMetadataCatalogEntry],
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

        checksum = get_file_checksum(impl_file_path)
        udf_entry = self._udf_service.insert_entry(name, impl_file_path, type, checksum)
        for udf_io in udf_io_list:
            udf_io.udf_id = udf_entry.row_id
        self._udf_io_service.insert_entries(udf_io_list)
        for udf_metadata in udf_metadata_list:
            udf_metadata.udf_id = udf_entry.row_id
        self._udf_metadata_service.insert_entries(udf_metadata_list)
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

    "udf cost catalog services"

    def upsert_udf_cost_catalog_entry(
        self, udf_id: int, name: str, cost: int
    ) -> UdfCostCatalogEntry:
        """Upserts UDF cost catalog entry.

        Arguments:
            udf_id(int): unique udf id
            name(str): the name of the udf
            cost(int): cost of this UDF

        Returns:
            The persisted UdfCostCatalogEntry object.
        """

        self._udf_cost_catalog_service.upsert_entry(udf_id, name, cost)

    def get_udf_cost_catalog_entry(self, name: str):
        return self._udf_cost_catalog_service.get_entry_by_name(name)

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
        vector_store_type: VectorStoreType,
        feat_column: ColumnCatalogEntry,
        udf_signature: str,
    ) -> IndexCatalogEntry:
        index_catalog_entry = self._index_service.insert_entry(
            name, save_file_path, vector_store_type, feat_column, udf_signature
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

    """ Udf Cache related"""

    def insert_udf_cache_catalog_entry(self, func_expr: FunctionExpression):
        cache_dir = self._config.get_value("storage", "cache_dir")
        entry = construct_udf_cache_catalog_entry(func_expr, cache_dir=cache_dir)
        return self._udf_cache_service.insert_entry(entry)

    def get_udf_cache_catalog_entry_by_name(self, name: str) -> UdfCacheCatalogEntry:
        return self._udf_cache_service.get_entry_by_name(name)

    def drop_udf_cache_catalog_entry(self, entry: UdfCacheCatalogEntry) -> bool:
        # remove the data structure associated with the entry
        if entry:
            shutil.rmtree(entry.cache_path)
        return self._udf_cache_service.delete_entry(entry)

    """ UDF Metadata Catalog"""

    def get_udf_metadata_entries_by_udf_name(
        self, udf_name: str
    ) -> List[UdfMetadataCatalogEntry]:
        """
        Get the UDF metadata information for the provided udf.

        Arguments:
             udf_name (str): name of the UDF

        Returns:
            UdfMetadataCatalogEntry objects
        """
        udf_entry = self.get_udf_catalog_entry_by_name(udf_name)
        if udf_entry:
            entries = self._udf_metadata_service.get_entries_by_udf_id(udf_entry.row_id)
            return entries
        else:
            return []

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

        dataset_location = self._config.get_value("core", "datasets_dir")
        file_url = str(generate_file_path(dataset_location, table_name))
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
        assert format_type in [
            FileFormatType.VIDEO,
            FileFormatType.IMAGE,
            FileFormatType.DOCUMENT,
            FileFormatType.PDF,
        ], f"Format Type {format_type} is not supported"

        if format_type is FileFormatType.VIDEO:
            columns = get_video_table_column_definitions()
            table_type = TableType.VIDEO_DATA
        elif format_type is FileFormatType.IMAGE:
            columns = get_image_table_column_definitions()
            table_type = TableType.IMAGE_DATA
        elif format_type is FileFormatType.DOCUMENT:
            columns = get_document_table_column_definitions()
            table_type = TableType.DOCUMENT_DATA
        elif format_type is FileFormatType.PDF:
            columns = get_pdf_table_column_definitions()
            table_type = TableType.PDF_DATA

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
        assert (
            obj is not None
        ), f"Table with name {media_metadata_name} does not exist in catalog"

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
        assert obj is None, "Table with name {media_metadata_name} already exists"

        columns = [ColumnDefinition("file_url", ColumnType.TEXT, None, None)]
        obj = self.create_and_insert_table_catalog_entry(
            TableInfo(media_metadata_name),
            columns,
            identifier_column=columns[0].name,
            table_type=TableType.SYSTEM_STRUCTURED_DATA,
        )
        return obj


#### get catalog instance
# This function plays a crucial role in ensuring that different threads do
# not share the same catalog object, as it can result in serialization issues and
# incorrect behavior with SQLAlchemy. Therefore, whenever a catalog instance is
# required, we create a new one. One possible optimization is to share the catalog
# instance across all objects within the same thread. It is worth investigating whether
# SQLAlchemy already handles this optimization for us, which will be explored at a
# later time.
def get_catalog_instance(db_uri: str, config: ConfigurationManager):
    return CatalogManager(db_uri, config)
