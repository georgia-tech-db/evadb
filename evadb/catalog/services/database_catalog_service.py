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

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from evadb.catalog.models.database_catalog import DatabaseCatalog
from evadb.catalog.models.utils import DatabaseCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class DatabaseCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(DatabaseCatalog, db_session)

    def insert_entry(
        self,
        name: str,
        engine: str,
        params: dict,
    ):
        try:
            db_catalog_obj = self.model(
                name=name,
                engine=engine,
                params=params,
            )
            db_catalog_obj = db_catalog_obj.save(self.session)

        except Exception as e:
            logger.exception(
                f"Failed to insert entry into database catalog with exception {str(e)}"
            )
            raise CatalogError(e)

    def get_entry_by_name(self, database_name: str) -> DatabaseCatalogEntry:
        """
        Get the table catalog entry with given table name.
        Arguments:
            database_name  (str): Database name
        Returns:
            DatabaseCatalogEntry - catalog entry for given database name
        """
        entry = self.session.execute(
            select(self.model).filter(self.model._name == database_name)
        ).scalar_one_or_none()
        if entry:
            return entry.as_dataclass()
        return entry

    def delete_entry(self, database_entry: DatabaseCatalogEntry):
        """Delete database from the catalog
        Arguments:
            database  (DatabaseCatalogEntry): database to delete
        Returns:
            True if successfully removed else false
        """
        try:
            db_catalog_obj = self.session.execute(
                select(self.model).filter(self.model._row_id == database_entry.row_id)
            ).scalar_one_or_none()
            db_catalog_obj.delete(self.session)
            return True
        except Exception as e:
            err_msg = (
                f"Delete database failed for {database_entry} with error {str(e)}."
            )
            logger.exception(err_msg)
            raise CatalogError(err_msg)
