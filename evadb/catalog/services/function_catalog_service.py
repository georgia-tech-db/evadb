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

from evadb.catalog.models.function_catalog import FunctionCatalog, FunctionCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.logging_manager import logger


class FunctionCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(FunctionCatalog, db_session)

    def insert_entry(
        self, name: str, impl_path: str, type: str, checksum: str
    ) -> FunctionCatalogEntry:
        """Insert a new function entry

        Arguments:
            name (str): name of the function
            impl_path (str): path to the function implementation relative to evadb/function
            type (str): function operator kind, classification or detection or etc
            checksum(str): checksum of the function file content, used for consistency

        Returns:
            FunctionCatalogEntry: Returns the new entry created
        """
        function_obj = self.model(name, impl_path, type, checksum)
        function_obj = function_obj.save(self.session)
        return function_obj.as_dataclass()

    def get_entry_by_name(self, name: str) -> FunctionCatalogEntry:
        """return the function entry that matches the name provided.
           None if no such entry found.

        Arguments:
            name (str): name to be searched
        """

        function_obj = self.session.execute(
            select(self.model).filter(self.model._name == name)
        ).scalar_one_or_none()
        if function_obj:
            return function_obj.as_dataclass()
        return None

    def get_entry_by_id(self, id: int, return_alchemy=False) -> FunctionCatalogEntry:
        """return the function entry that matches the id provided.
           None if no such entry found.

        Arguments:
            id (int): id to be searched
        """

        function_obj = self.session.execute(
            select(self.model).filter(self.model._row_id == id)
        ).scalar_one_or_none()
        if function_obj:
            return function_obj if return_alchemy else function_obj.as_dataclass()
        return function_obj

    def delete_entry_by_name(self, name: str):
        """Delete a function entry from the catalog FunctionCatalog

        Arguments:
            name (str): function name to be deleted

        Returns:
            True if successfully deleted else True
        """
        try:
            function_obj = self.session.execute(
                select(self.model).filter(self.model._name == name)
            ).scalar_one()
            function_obj.delete(self.session)
        except Exception as e:
            logger.exception(
                f"Delete function failed for name {name} with error {str(e)}"
            )
            return False
        return True
