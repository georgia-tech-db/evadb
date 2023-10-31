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

from evadb.catalog.models.configuration_catalog import ConfigurationCatalog
from evadb.catalog.models.utils import ConfigurationCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class ConfigurationCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(ConfigurationCatalog, db_session)

    def insert_entry(
        self,
        key: str,
        value: any,
    ):
        try:
            config_catalog_obj = self.model(key=key, value=value)
            config_catalog_obj = config_catalog_obj.save(self.session)

        except Exception as e:
            logger.exception(
                f"Failed to insert entry into database catalog with exception {str(e)}"
            )
            raise CatalogError(e)

    def get_entry_by_name(self, key: str) -> ConfigurationCatalogEntry:
        """
        Get the table catalog entry with given table name.
        Arguments:
            key  (str): key name
        Returns:
            Configuration Catalog Entry - catalog entry for given key name
        """
        entry = self.session.execute(
            select(self.model).filter(self.model._key == key)
        ).scalar_one_or_none()
        if entry:
            return entry.as_dataclass()
        return entry

    def upsert_entry(
        self,
        key: str,
        value: any,
    ):
        try:
            entry = self.session.execute(
                select(self.model).filter(self.model._key == key)
            ).scalar_one_or_none()
            if entry:
                entry.update(self.session, _value=value)
            else:
                self.insert_entry(key, value)
        except Exception as e:
            raise CatalogError(
                f"Error while upserting entry to ConfigurationCatalog: {str(e)}"
            )
