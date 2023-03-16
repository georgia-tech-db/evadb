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
from dataclasses import dataclass

from sqlalchemy import Column, ForeignKey, Integer, String

from eva.catalog.models.base_model import BaseModel


class UdfCostCatalog(BaseModel):
    """The `UdfCostCatalog` catalog stores information about the runtime of user-defined functions (UDFs)
    in the system. It maintains the following information for each UDF.
    `_name:` name of the UDF
    `_cost:` cost of this UDF
    """

    __tablename__ = "udf_cost_catalog"

    _cost = Column("cost", Integer())
    _udf_name = Column("name", String(100), ForeignKey("udf_catalog.name"))
    _udf_id = Column("udf_id", Integer(), ForeignKey("udf_catalog._row_id"))

    def __init__(self, udf_id: int, name: str, cost: int):
        self._udf_id = udf_id
        self._udf_name = name
        self._cost = cost

    def as_dataclass(self) -> "UdfCostCatalogEntry":
        return UdfCostCatalog(udf_id=self._udf_id, name=self._udf_name, cost=self._cost)


@dataclass(unsafe_hash=True)
class UdfCostCatalogEntry:
    """Dataclass representing an entry in the `UdfCostCatalog`.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    cost: int = None
    udf_id: int = None

    def display_format(self):
        return {"udf_id": self.udf_id, "name": self.name, "cost": self.cost}
