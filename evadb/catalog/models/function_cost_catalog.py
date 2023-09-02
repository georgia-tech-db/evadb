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

from sqlalchemy import Column, Float, ForeignKey, Integer, String

from evadb.catalog.models.base_model import BaseModel
from evadb.catalog.models.utils import FunctionCostCatalogEntry


class FunctionCostCatalog(BaseModel):
    """The `FunctionCostCatalog` catalog stores information about the runtime of user-defined functions (Functions) in the system. It maintains the following information for each Function.
    `_row_id:` an autogenerated unique identifier.
    `_name:` name of the Function
    `_function_id`: the row_id of the Function
    `_cost:` cost of this Function
    """

    __tablename__ = "function_cost_catalog"

    _function_id = Column(
        "function_id", Integer, ForeignKey("function_catalog._row_id", ondelete="CASCADE")
    )
    _function_name = Column(
        "name", String(128), ForeignKey("function_catalog.name", ondelete="CASCADE")
    )
    _cost = Column("cost", Float)

    def __init__(self, function_id: int, name: str, cost: float):
        self._function_id = function_id
        self._function_name = name
        self._cost = cost

    def as_dataclass(self) -> "FunctionCostCatalogEntry":
        return FunctionCostCatalogEntry(
            function_id=self._function_id,
            name=self._function_name,
            cost=self._cost,
            row_id=self._row_id,
        )
