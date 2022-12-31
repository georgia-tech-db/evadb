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
from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.catalog_type import TableType
from eva.catalog.models.table_catalog import TableCatalog
from eva.catalog.services.base_service import BaseService
from eva.utils.errors import CatalogError
from eva.utils.logging_manager import logger


class TableCatalogService(BaseService):
    def __init__(self):
        super().__init__(TableCatalog)

    def insert_entry(
        self, name: str, file_url: str, identifier_id, table_type: TableType
    ) -> TableCatalog:
        """Insert a new table entry into table catalog.
        Arguments:
            name (str): name of the table
            file_url (str): file path of the table.
            table_type (TableType): type of data in the table
        Returns:
            TableCatalog object
        """
        try:
            table_catalog_obj = self.model(
                name=name,
                file_url=file_url,
                identifier_id=identifier_id,
                table_type=table_type,
            )
            table_catalog_obj = table_catalog_obj.save()
        except Exception as e:
            logger.exception(
                f"Failed to insert entry into table catalog with exception {str(e)}"
            )
            raise CatalogError(e)
        else:
            return table_catalog_obj

    def get_entry_by_id(self, table_id) -> TableCatalog:
        """
        Returns the table by ID
        Arguments:
            table_id (int)
        Returns:
           TableCatalog
        """
        return self.model.query.filter(self.model._row_id == table_id).one()

    def get_entry_by_name(self, database_name, table_name):
        """
        Get the table catalog entry with given table name.
        Arguments:
            database_name  (str): Database to which table belongs # TODO:
            use this field
            table_name (str): name of the table
        Returns:
            TableCatalog - catalog entry for given table_name
        """
        return self.model.query.filter(self.model._name == table_name).one_or_none()

    def delete_entry(self, table: TableCatalog):
        """Delete table from the db
        Arguments:
            table  (TableCatalog): table to delete
        Returns:
            True if successfully removed else false
        """
        try:
            table.delete()
            return True
        except Exception as e:
            err_msg = f"Delete table failed for {table} with error {str(e)}."
            logger.exception(err_msg)
            raise CatalogError(err_msg)

    def rename_entry(self, table: TableCatalog, new_name: str):
        try:
            table.update(_name=new_name)
        except Exception as e:
            err_msg = "Update table name failed for {} with error {}".format(
                table.name, str(e)
            )
            logger.error(err_msg)
            raise RuntimeError(err_msg)

    def get_all_entries(self):
        try:
            return self.model.query.all()
        except NoResultFound:
            return []
