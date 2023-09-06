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

from evadb.catalog.models.function_cost_catalog import (
    FunctionCostCatalog,
    FunctionCostCatalogEntry,
)
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError


class FunctionCostCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(FunctionCostCatalog, db_session)

    def insert_entry(
        self, function_id: int, name: str, cost: int
    ) -> FunctionCostCatalogEntry:
        """Insert a new function cost entry

        Arguments:
            function_id(int): id of the function
            name (str) : name of the function
            cost(int)  : cost of the function

        Returns:
            FunctionCostCatalogEntry: Returns the new entry created
        """
        try:
            function_obj = self.model(function_id, name, cost)
            function_obj.save(self.session)
        except Exception as e:
            raise CatalogError(
                f"Error while inserting entry to FunctionCostCatalog: {str(e)}"
            )

    def upsert_entry(self, function_id: int, name: str, new_cost: int):
        """Upserts a new function cost entry

        Arguments:
            function_id(int): id of the function
            name (str) : name of the function
            cost(int)  : cost of the function
        """
        try:
            function_obj = self.session.execute(
                select(self.model).filter(self.model._function_id == function_id)
            ).scalar_one_or_none()
            if function_obj:
                function_obj.update(self.session, cost=new_cost)
            else:
                self.insert_entry(function_id, name, new_cost)
        except Exception as e:
            raise CatalogError(
                f"Error while upserting entry to FunctionCostCatalog: {str(e)}"
            )

    def get_entry_by_name(self, name: str) -> FunctionCostCatalogEntry:
        """return the function cost entry that matches the name provided.
           None if no such entry found.

        Arguments:
            name (str): name to be searched
        """

        try:
            function_obj = self.session.execute(
                select(self.model).filter(self.model._function_name == name)
            ).scalar_one_or_none()
            if function_obj:
                return function_obj.as_dataclass()
            return None
        except Exception as e:
            raise CatalogError(
                f"Error while getting entry for function {name} from FunctionCostCatalog: {str(e)}"
            )
