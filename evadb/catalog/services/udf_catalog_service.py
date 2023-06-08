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

from evadb.catalog.models.udf_catalog import UdfCatalog, UdfCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.logging_manager import logger


class UdfCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(UdfCatalog, db_session)

    def insert_entry(
        self, name: str, impl_path: str, type: str, checksum: str
    ) -> UdfCatalogEntry:
        """Insert a new udf entry

        Arguments:
            name (str): name of the udf
            impl_path (str): path to the udf implementation relative to evadb/udf
            type (str): udf operator kind, classification or detection or etc
            checksum(str): checksum of the udf file content, used for consistency

        Returns:
            UdfCatalogEntry: Returns the new entry created
        """
        udf_obj = self.model(name, impl_path, type, checksum)
        udf_obj = udf_obj.save(self.session)
        return udf_obj.as_dataclass()

    def get_entry_by_name(self, name: str) -> UdfCatalogEntry:
        """return the udf entry that matches the name provided.
           None if no such entry found.

        Arguments:
            name (str): name to be searched
        """

        udf_obj = self.session.execute(
            select(self.model).filter(self.model._name == name)
        ).scalar_one_or_none()
        if udf_obj:
            return udf_obj.as_dataclass()
        return None

    def get_entry_by_id(self, id: int, return_alchemy=False) -> UdfCatalogEntry:
        """return the udf entry that matches the id provided.
           None if no such entry found.

        Arguments:
            id (int): id to be searched
        """

        udf_obj = self.session.execute(
            select(self.model).filter(self.model._row_id == id)
        ).scalar_one_or_none()
        if udf_obj:
            return udf_obj if return_alchemy else udf_obj.as_dataclass()
        return udf_obj

    def delete_entry_by_name(self, name: str):
        """Delete a udf entry from the catalog UdfCatalog

        Arguments:
            name (str): udf name to be deleted

        Returns:
            True if successfully deleted else True
        """
        try:
            udf_obj = self.session.execute(
                select(self.model).filter(self.model._name == name)
            ).scalar_one()
            udf_obj.delete(self.session)
        except Exception as e:
            logger.exception(f"Delete udf failed for name {name} with error {str(e)}")
            return False
        return True
