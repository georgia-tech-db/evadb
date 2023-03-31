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

from eva.catalog.models.udf_cost_catalog import UdfCostCatalog, UdfCostCatalogEntry
from eva.catalog.services.base_service import BaseService
from eva.utils.errors import CatalogError


class UdfCostCatalogService(BaseService):
    def __init__(self):
        super().__init__(UdfCostCatalog)

    def insert_entry(self, udf_id: int, name: str, cost: int) -> UdfCostCatalogEntry:
        """Insert a new udf cost entry

        Arguments:
            udf_id(int): id of the udf
            name (str) : name of the udf
            cost(int)  : cost of the udf

        Returns:
            UdfCostCatalogEntry: Returns the new entry created
        """
        try:
            udf_obj = self.model(udf_id, name, cost)
            udf_obj.save()
        except Exception as e:
            raise CatalogError(
                f"Error while inserting entry to UdfCostCatalog: {str(e)}"
            )

    def upsert_entry(self, udf_id: int, name: str, new_cost: int):
        """Upserts a new udf cost entry

        Arguments:
            udf_id(int): id of the udf
            name (str) : name of the udf
            cost(int)  : cost of the udf
        """
        try:
            udf_obj = self.model.query.filter(
                self.model._udf_id == udf_id
            ).one_or_none()
            if udf_obj:
                udf_obj.update(cost=new_cost)
            else:
                self.insert_entry(udf_id, name, new_cost)
        except Exception as e:
            raise CatalogError(
                f"Error while upserting entry to UdfCostCatalog: {str(e)}"
            )

    def get_entry_by_name(self, name: str) -> UdfCostCatalogEntry:
        """return the udf cost entry that matches the name provided.
           None if no such entry found.

        Arguments:
            name (str): name to be searched
        """

        try:
            udf_obj = self.model.query.filter(
                self.model._udf_name == name
            ).one_or_none()
            if udf_obj:
                return udf_obj.as_dataclass()
            return None
        except Exception as e:
            raise CatalogError(
                f"Error while getting entry for udf {name} from UdfCostCatalog: {str(e)}"
            )
