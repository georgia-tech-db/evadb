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

from src.catalog.database import init_db
from src.catalog.df_schema import DataFrameSchema
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

        # eva_dir = ConfigurationManager().get_value("core", "location")
        # output_url = os.path.join(eva_dir, CATALOG_DIR)
        # LoggingManager().log("Bootstrapping catalog" + str(output_url),
        #                      LoggingLevel.INFO)
        LoggingManager().log("Bootstrapping catalog", LoggingLevel.INFO)
        init_db()
        # # Construct output location
        # catalog_dir_url = os.path.join(eva_dir, "catalog")
        #
        # # Get filesystem path
        # catalog_os_path = urlparse(catalog_dir_url).path
        #
        # # Check if catalog exists
        # if os.path.exists(catalog_os_path):
        #     # Load catalog if it exists
        #     load_catalog_dataframes(catalog_dir_url,
        #     self._catalog_dictionary)
        # else:
        #     # Create catalog if it does not exist
        #     create_catalog_dataframes(
        #         catalog_dir_url, self._catalog_dictionary)

    def get_table_bindings(self, database_name: str, table_name: str,
                           column_names: List[str]) -> Tuple[int, List[int]]:
        """
        This method fetches bindings for strings
        :param database_name: currently not in use
        :param table_name: the table that is being referred to
        :param column_names: the column names of the table for which
        bindings are required
        :return: returns metadat_id of table and a list of column ids
        """

        metadata_id = DataFrameMetadata.get_id_from_name(table_name)
        column_ids = []
        if column_names is not None:
            column_ids = DataFrameColumn.get_id_from_metadata_id_and_name_in(
                metadata_id,
                column_names)
        return metadata_id, column_ids

    def get_metadata(self, metadata_id: int,
                     col_id_list: List[int] = None) -> DataFrameMetadata:
        """
        This method returns the metadata object given a metadata_id,
        when requested by the executor. It will further be used by storage
        engine for retrieving the dataframe.
        :param metadata_id: metadata id of the table
        :param col_id_list: optional column ids of the table referred
        :return:
        """
        metadata = DataFrameMetadata.get(metadata_id)
        if col_id_list is not None:
            df_columns = DataFrameColumn.get_by_metadata_id_and_id_in(
                col_id_list,
                metadata_id)
            metadata.set_schema(
                DataFrameSchema(metadata.get_name(), df_columns))
        return metadata


    def get_column_types(self, table_metadata_id: int, col_id_list: List[int]) -> List[ColumnType]:
        """
        This method consumes the input table_id and the input column_id_list and
        returns a list of ColumnType for each provided column_id.
        
        Arguments:
            table_metadata_id {int} -- [metadata_id of the table]
            col_id_list {List[int]} -- [metadata ids of the columns; If list = None, return type for all columns in the table]
        
        Returns:
            List[ColumnType] -- [list of required column type for each input column]
        """
        metadata = DataFrameMetadata.get(table_metadata_id)
        col_types = []
        df_columns = DataFrameColumn.get_by_metadata_id_and_id_in(
                col_id_list,
                metadata_id)
        for col in df_columns:
            col_types.append(col.get_type())
        
        return col_types
            
    def get_column_ids(self, table_metadata_id: int) -> List[int]:
        """
        This method returns all the column_ids associated with the given table_metadata_id
        
        Arguments:
            table_metadata_id {int} -- [table metadata id for which columns are required]
        
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


if __name__ == '__main__':
    catalog = CatalogManager()
    metadata_id, col_ids = catalog.get_table_bindings(None, 'dataset1',
                                                      ['frame', 'color'])
    metadata = catalog.get_metadata(1, [1])
    print(metadata.get_dataframe_schema())
    print(metadata_id, col_ids)
