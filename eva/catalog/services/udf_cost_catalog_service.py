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
from typing import List

from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.models.udf_cost_catalog import UdfCostCatalog, UdfCostCatalogEntry
from eva.catalog.services.base_service import BaseService


class UdfCostCatalogService(BaseService):
    def __init__(self):
        super().__init__(UdfCostCatalog)

    def insert_entry(self, name: str, cost: int) -> UdfCostCatalogEntry:
        """Insert a new udf cost entry

        Arguments:
            name (str): name of the udf
            cost(int) : cost of the udf

        Returns:
            UdfCostCatalogEntry: Returns the new entry created
        """
        udf_obj = self.model(name, cost)
        udf_obj = udf_obj.save()
        return udf_obj.as_dataclass()

    def get_entry_by_name(self, name: str) -> UdfCostCatalogEntry:
        """return the udf cost entry that matches the name provided.
           None if no such entry found.

        Arguments:
            name (str): name to be searched
        """

        try:
            udf_obj = self.model.query.filter(self.model._name == name).one()
            if udf_obj:
                return udf_obj.as_dataclass()
            return udf_obj
        except NoResultFound:
            return None

    def get_all_entries(self) -> List[UdfCostCatalogEntry]:
        try:
            objs = self.model.query.all()
            return [obj.as_dataclass() for obj in objs]
        except NoResultFound:
            return []
