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
import datetime
import shutil
from pathlib import Path
from typing import Any, List

from evadb.catalog.catalog_type import (
    ColumnType,
    TableType,
    VectorStoreType,
    VideoColumnName,
)
from evadb.catalog.catalog_utils import (
    construct_function_cache_catalog_entry,
    get_document_table_column_definitions,
    get_image_table_column_definitions,
    get_pdf_table_column_definitions,
    get_video_table_column_definitions,
    xform_column_definitions_to_catalog_entries,
)
from evadb.catalog.models.utils import (
    ColumnCatalogEntry,
    DatabaseCatalogEntry,
    FunctionCacheCatalogEntry,
    FunctionCatalogEntry,
    FunctionCostCatalogEntry,
    FunctionIOCatalogEntry,
    FunctionMetadataCatalogEntry,
    IndexCatalogEntry,
    JobCatalogEntry,
    JobHistoryCatalogEntry,
    TableCatalogEntry,
    drop_all_tables_except_catalog,
    init_db,
    truncate_catalog_tables,
)
from evadb.catalog.services.column_catalog_service import ColumnCatalogService
from evadb.catalog.services.configuration_catalog_service import (
    ConfigurationCatalogService,
)
from evadb.catalog.services.database_catalog_service import DatabaseCatalogService
from evadb.catalog.services.function_cache_catalog_service import (
    FunctionCacheCatalogService,
)
from evadb.catalog.services.function_catalog_service import FunctionCatalogService
from evadb.catalog.services.function_cost_catalog_service import (
    FunctionCostCatalogService,
)
from evadb.catalog.services.function_io_catalog_service import FunctionIOCatalogService
from evadb.catalog.services.function_metadata_catalog_service import (
    FunctionMetadataCatalogService,
)
from evadb.catalog.services.index_catalog_service import IndexCatalogService
from evadb.catalog.services.job_catalog_service import JobCatalogService
from evadb.catalog.services.job_history_catalog_service import JobHistoryCatalogService
from evadb.catalog.services.table_catalog_service import TableCatalogService
from evadb.catalog.sql_config import IDENTIFIER_COLUMN, SQLConfig
from evadb.expression.function_expression import FunctionExpression
from evadb.parser.create_statement import ColumnDefinition
from evadb.parser.table_ref import TableInfo
from evadb.parser.types import FileFormatType
from evadb.third_party.databases.interface import get_database_handler
from evadb.utils.generic_utils import (
    generate_file_path,
    get_file_checksum,
    remove_directory_contents,
)
from evadb.utils.logging_manager import logger


class CatalogManager(object):
    def __init__(self, db_uri: str):
        self._db_uri = db_uri
        self._sql_config = SQLConfig(db_uri)
        self._bootstrap_catalog()
        self._db_catalog_service = DatabaseCatalogService(self._sql_config.session)
        self._config_catalog_service = ConfigurationCatalogService(
            self._sql_config.session
        )
        self._job_catalog_service = JobCatalogService(self._sql_config.session)
        self._job_history_catalog_service = JobHistoryCatalogService(
            self._sql_config.session
        )
        self._table_catalog_service = TableCatalogService(self._sql_config.session)
        self._column_service = ColumnCatalogService(self._sql_config.session)
        self._function_service = FunctionCatalogService(self._sql_config.session)
        self._function_cost_catalog_service = FunctionCostCatalogService(
            self._sql_config.session
        )
        self._function_io_service = FunctionIOCatalogService(self._sql_config.session)
        self._function_metadata_service = FunctionMetadataCatalogService(
            self._sql_config.session
        )
        self._index_service = IndexCatalogService(self._sql_config.session)
        self._function_cache_service = FunctionCacheCatalogService(
            self._sql_config.session
        )

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
        # truncate the catalog tables except configuration_catalog
        # We do not remove the configuration entries
        truncate_catalog_tables(
            self._sql_config.engine, tables_not_to_truncate=["configuration_catalog"]
        )
        # clean up the dataset, index, and cache directories
        for folder in ["cache_dir", "index_dir", "datasets_dir"]:
            remove_directory_contents(self.get_configuration_catalog_value(folder))

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

    def get_all_database_catalog_entries(self):
        return self._db_catalog_service.get_all_entries()

    def drop_database_catalog_entry(self, database_entry: DatabaseCatalogEntry) -> bool:
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

    def check_native_table_exists(self, table_name: str, database_name: str):
        """
        Validate the database is valid and the requested table in database is
        also valid.
        """
        db_catalog_entry = self.get_database_catalog_entry(database_name)

        if db_catalog_entry is None:
            return False

        with get_database_handler(
            db_catalog_entry.engine, **db_catalog_entry.params
        ) as handler:
            # Get table definition.
            resp = handler.get_tables()

            if resp.error is not None:
                raise Exception(resp.error)

            # Check table existence.
            table_df = resp.data
            if table_name not in table_df["table_name"].values:
                return False

        return True

    "Job catalog services"

    def insert_job_catalog_entry(
        self,
        name: str,
        queries: str,
        start_time: datetime,
        end_time: datetime,
        repeat_interval: int,
        active: bool,
        next_schedule_run: datetime,
    ) -> JobCatalogEntry:
        """A new entry is persisted in the job catalog.

        Args:
            name: job name
            queries: job's queries
            start_time: job start time
            end_time: job end time
            repeat_interval: job repeat interval
            active: job status
            next_schedule_run: next run time as per schedule
        """
        job_entry = self._job_catalog_service.insert_entry(
            name,
            queries,
            start_time,
            end_time,
            repeat_interval,
            active,
            next_schedule_run,
        )

        return job_entry

    def get_job_catalog_entry(self, job_name: str) -> JobCatalogEntry:
        """
        Returns the job catalog entry for the given database_name
        Arguments:
            job_name (str): name of the job

        Returns:
            JobCatalogEntry
        """

        table_entry = self._job_catalog_service.get_entry_by_name(job_name)

        return table_entry

    def drop_job_catalog_entry(self, job_entry: JobCatalogEntry) -> bool:
        """
        This method deletes the job from  catalog.

        Arguments:
           job_entry: job catalog entry to remove

        Returns:
           True if successfully deleted else False
        """
        return self._job_catalog_service.delete_entry(job_entry)

    def get_next_executable_job(self, only_past_jobs: bool = False) -> JobCatalogEntry:
        """Get the oldest job that is ready to be triggered by trigger time
        Arguments:
            only_past_jobs: boolean flag to denote if only jobs with trigger time in
                past should be considered
        Returns:
            Returns the first job to be triggered
        """
        return self._job_catalog_service.get_next_executable_job(only_past_jobs)

    def update_job_catalog_entry(
        self, job_name: str, next_scheduled_run: datetime, active: bool
    ):
        """Update the next_scheduled_run and active column as per the provided values
        Arguments:
            job_name (str): job which should be updated

            next_run_time (datetime): the next trigger time for the job

            active (bool): the active status for the job
        """
        self._job_catalog_service.update_next_scheduled_run(
            job_name, next_scheduled_run, active
        )

    "Job history catalog services"

    def insert_job_history_catalog_entry(
        self,
        job_id: str,
        job_name: str,
        execution_start_time: datetime,
        execution_end_time: datetime,
    ) -> JobCatalogEntry:
        """A new entry is persisted in the job history catalog.

        Args:
            job_id: job id for the execution entry
            job_name: job name for the execution entry
            execution_start_time: job execution start time
            execution_end_time: job execution end time
        """
        job_history_entry = self._job_history_catalog_service.insert_entry(
            job_id, job_name, execution_start_time, execution_end_time
        )

        return job_history_entry

    def get_job_history_by_job_id(self, job_id: int) -> List[JobHistoryCatalogEntry]:
        """Returns all the entries present for this job_id on in the history.

        Args:
            job_id: the id of job whose history should be fetched
        """
        return self._job_history_catalog_service.get_entry_by_job_id(job_id)

    def update_job_history_end_time(
        self, job_id: int, execution_start_time: datetime, execution_end_time: datetime
    ) -> List[JobHistoryCatalogEntry]:
        """Updates the execution_end_time for this job history matching job_id and execution_start_time.

        Args:
            job_id: id of the job whose history entry which should be updated
            execution_start_time: the start time for the job history entry
            execution_end_time: the end time for the job history entry
        """
        return self._job_history_catalog_service.update_entry_end_time(
            job_id, execution_start_time, execution_end_time
        )

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
        is_native_table = database_name is not None

        if is_native_table:
            return self.check_native_table_exists(table_name, database_name)
        else:
            table_entry = self._table_catalog_service.get_entry_by_name(
                database_name, table_name
            )
            return table_entry is not None

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

    "function catalog services"

    def insert_function_catalog_entry(
        self,
        name: str,
        impl_file_path: str,
        type: str,
        function_io_list: List[FunctionIOCatalogEntry],
        function_metadata_list: List[FunctionMetadataCatalogEntry],
    ) -> FunctionCatalogEntry:
        """Inserts a function catalog entry along with Function_IO entries.
        It persists the entry to the database.

        Arguments:
            name(str): name of the function
            impl_file_path(str): implementation path of the function
            type(str): what kind of function operator like classification,
                                                        detection etc
            function_io_list(List[FunctionIOCatalogEntry]): input/output function info list

        Returns:
            The persisted FunctionCatalogEntry object.
        """

        checksum = get_file_checksum(impl_file_path)
        function_entry = self._function_service.insert_entry(
            name,
            impl_file_path,
            type,
            checksum,
            function_io_list,
            function_metadata_list,
        )
        return function_entry

    def get_function_catalog_entry_by_name(self, name: str) -> FunctionCatalogEntry:
        """
        Get the function information based on name.

        Arguments:
             name (str): name of the function

        Returns:
            FunctionCatalogEntry object
        """
        return self._function_service.get_entry_by_name(name)

    def delete_function_catalog_entry_by_name(self, function_name: str) -> bool:
        return self._function_service.delete_entry_by_name(function_name)

    def get_all_function_catalog_entries(self):
        return self._function_service.get_all_entries()

    "function cost catalog services"

    def upsert_function_cost_catalog_entry(
        self, function_id: int, name: str, cost: int
    ) -> FunctionCostCatalogEntry:
        """Upserts function cost catalog entry.

        Arguments:
            function_id(int): unique function id
            name(str): the name of the function
            cost(int): cost of this function

        Returns:
            The persisted FunctionCostCatalogEntry object.
        """

        self._function_cost_catalog_service.upsert_entry(function_id, name, cost)

    def get_function_cost_catalog_entry(self, name: str):
        return self._function_cost_catalog_service.get_entry_by_name(name)

    "FunctionIO services"

    def get_function_io_catalog_input_entries(
        self, function_obj: FunctionCatalogEntry
    ) -> List[FunctionIOCatalogEntry]:
        return self._function_io_service.get_input_entries_by_function_id(
            function_obj.row_id
        )

    def get_function_io_catalog_output_entries(
        self, function_obj: FunctionCatalogEntry
    ) -> List[FunctionIOCatalogEntry]:
        return self._function_io_service.get_output_entries_by_function_id(
            function_obj.row_id
        )

    """ Index related services. """

    def insert_index_catalog_entry(
        self,
        name: str,
        save_file_path: str,
        vector_store_type: VectorStoreType,
        feat_column: ColumnCatalogEntry,
        function_signature: str,
        index_def: str,
    ) -> IndexCatalogEntry:
        index_catalog_entry = self._index_service.insert_entry(
            name,
            save_file_path,
            vector_store_type,
            feat_column,
            function_signature,
            index_def,
        )
        return index_catalog_entry

    def get_index_catalog_entry_by_name(self, name: str) -> IndexCatalogEntry:
        return self._index_service.get_entry_by_name(name)

    def get_index_catalog_entry_by_column_and_function_signature(
        self, column: ColumnCatalogEntry, function_signature: str
    ):
        return self._index_service.get_entry_by_column_and_function_signature(
            column, function_signature
        )

    def drop_index_catalog_entry(self, index_name: str) -> bool:
        return self._index_service.delete_entry_by_name(index_name)

    def get_all_index_catalog_entries(self):
        return self._index_service.get_all_entries()

    """ Function Cache related"""

    def insert_function_cache_catalog_entry(self, func_expr: FunctionExpression):
        cache_dir = self.get_configuration_catalog_value("cache_dir")
        entry = construct_function_cache_catalog_entry(func_expr, cache_dir=cache_dir)
        return self._function_cache_service.insert_entry(entry)

    def get_function_cache_catalog_entry_by_name(
        self, name: str
    ) -> FunctionCacheCatalogEntry:
        return self._function_cache_service.get_entry_by_name(name)

    def drop_function_cache_catalog_entry(
        self, entry: FunctionCacheCatalogEntry
    ) -> bool:
        # remove the data structure associated with the entry
        if entry:
            shutil.rmtree(entry.cache_path)
        return self._function_cache_service.delete_entry(entry)

    """ function Metadata Catalog"""

    def get_function_metadata_entries_by_function_name(
        self, function_name: str
    ) -> List[FunctionMetadataCatalogEntry]:
        """
        Get the function metadata information for the provided function.

        Arguments:
             function_name (str): name of the function

        Returns:
            FunctionMetadataCatalogEntry objects
        """
        function_entry = self.get_function_catalog_entry_by_name(function_name)
        if function_entry:
            entries = self._function_metadata_service.get_entries_by_function_id(
                function_entry.row_id
            )
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

        dataset_location = self.get_configuration_catalog_value("datasets_dir")
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

    "Configuration catalog services"

    def upsert_configuration_catalog_entry(self, key: str, value: any):
        """Upserts configuration catalog entry"

        Args:
            key: key name
            value: value name
        """
        self._config_catalog_service.upsert_entry(key, value)

    def get_configuration_catalog_value(self, key: str, default: Any = None) -> Any:
        """
        Returns the value entry for the given key
        Arguments:
            key (str): key name

        Returns:
            ConfigurationCatalogEntry
        """

        table_entry = self._config_catalog_service.get_entry_by_name(key)
        if table_entry:
            return table_entry.value
        return default
