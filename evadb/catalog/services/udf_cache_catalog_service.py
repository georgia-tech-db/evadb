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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import select

from evadb.catalog.models.udf_cache_catalog import UdfCacheCatalog
from evadb.catalog.models.utils import UdfCacheCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.catalog.services.column_catalog_service import ColumnCatalogService
from evadb.catalog.services.udf_catalog_service import UdfCatalogService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class UdfCacheCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(UdfCacheCatalog, db_session)
        self._column_service: ColumnCatalogService = ColumnCatalogService(db_session)
        self._udf_service: UdfCatalogService = UdfCatalogService(db_session)

    def insert_entry(self, entry: UdfCacheCatalogEntry) -> UdfCacheCatalogEntry:
        """Insert a new udf cache entry into udf cache catalog.
        Arguments:
            `name` (str): name of the cache table
            `udf_id` (int): `row_id` of the UDF on which the cache is built
            `cache_path` (str): path of the cache table
            `args` (List[Any]): arguments of the UDF whose output is being cached
            `udf_depends` (List[UdfCatalogEntry]): dependent UDF  entries
            `col_depends` (List[ColumnCatalogEntry]): dependent column entries
        Returns:
            `UdfCacheCatalogEntry`
        """
        try:
            cache_obj = self.model(
                name=entry.name,
                udf_id=entry.udf_id,
                cache_path=entry.cache_path,
                args=entry.args,
            )

            cache_obj._udf_depends = [
                self._udf_service.get_entry_by_id(udf_id, return_alchemy=True)
                for udf_id in entry.udf_depends
            ]
            cache_obj._col_depends = [
                self._column_service.get_entry_by_id(col_id, return_alchemy=True)
                for col_id in entry.col_depends
            ]
            cache_obj = cache_obj.save(self.session)

        except Exception as e:
            err_msg = (
                f"Failed to insert entry into udf cache catalog with exception {str(e)}"
            )
            logger.exception(err_msg)
            raise CatalogError(err_msg)
        else:
            return cache_obj.as_dataclass()

    def get_entry_by_name(self, name: str) -> UdfCacheCatalogEntry:
        try:
            entry = self.session.execute(
                select(self.model).filter(self.model._name == name)
            ).scalar_one()
            return entry.as_dataclass()
        except NoResultFound:
            return None

    def delete_entry(self, cache: UdfCacheCatalogEntry):
        """Delete cache table from the db
        Arguments:
            cache  (UdfCacheCatalogEntry): cache to delete
        Returns:
            True if successfully removed else false
        """
        try:
            obj = self.session.execute(
                select(self.model).filter(self.model._row_id == cache.row_id)
            ).scalar_one()
            obj.delete(self.session)
            return True
        except Exception as e:
            err_msg = f"Delete cache failed for {cache} with error {str(e)}."
            logger.exception(err_msg)
            raise CatalogError(err_msg)
