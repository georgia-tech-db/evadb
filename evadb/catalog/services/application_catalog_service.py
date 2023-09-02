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

from evadb.catalog.models.application_catalog import ApplicationCatalog
from evadb.catalog.models.utils import ApplicationCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class ApplicationCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(ApplicationCatalog, db_session)

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
                f"Failed to insert entry into application catalog with exception {str(e)}"
            )
            raise CatalogError(e)

    def get_entry_by_name(self, application_name: str) -> ApplicationCatalogEntry:
        """
        Get the table catalog entry with given table name.
        Arguments:
            application_name  (str): Application name
        Returns:
            ApplicationCatalogEntry - catalog entry for given application name
        """
        entry = self.session.execute(
            select(self.model).filter(self.model._name == application_name)
        ).scalar_one_or_none()
        if entry:
            return entry.as_dataclass()
        return entry

    def delete_entry(self, application_entry: ApplicationCatalogEntry):
        """Delete application from the catalog
        Arguments:
            application  (ApplicationCatalogEntry): application to delete
        Returns:
            True if successfully removed else false
        """
        try:
            db_catalog_obj = self.session.execute(
                select(self.model).filter(
                    self.model._row_id == application_entry.row_id
                )
            ).scalar_one_or_none()
            db_catalog_obj.delete(self.session)
            return True
        except Exception as e:
            err_msg = f"Delete application failed for {application_entry} with error {str(e)}."
            logger.exception(err_msg)
            raise CatalogError(err_msg)
