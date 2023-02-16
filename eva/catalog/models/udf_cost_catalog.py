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

from sqlalchemy import Column, Integer, String

from eva.catalog.models.base_model import BaseModel

# from sqlalchemy.orm import relationship


class UdfCostCatalog(BaseModel):
    """The `UdfCostCatalog` catalog stores information about the runtime of user-defined functions (UDFs)
    in the system. It maintains the following information for each UDF.
    TODO: add params

    """

    __tablename__ = "udf_cost_catalog"

    _type = Column("type", String(100))
    _cost = Column("cost", Integer())
    _frame_count = Column("frame_count", Integer())
    _resolution = Column("resolution", Integer())

    # TODO: Add hardware information - GPU information etc. - It can be its own table.

    # TODO: UdfCatalog storing the input/output attributes of the udf
    # _name = relationship(
    #     "UdfCatlog", back_populates="_name", cascade="all, delete, delete-orphan"
    # )

    _name = Column("name", String(100))

    def __init__(
        self, name: str, type: str, cost: int, frame_count: int, resolution: int
    ):
        self._name = name
        self._type = type
        self._cost = cost
        self._frame_count = frame_count
        self._resolution = resolution

    def as_dataclass(self) -> "UdfCostCatalogEntry":
        return UdfCostCatalog(
            name=self._name,
            type=self._type,
            cost=self._cost,
            frame_count=self._frame_count,
            resolution=self._resolution,
        )


@dataclass(unsafe_hash=True)
class UdfCostCatalogEntry:
    """Dataclass representing an entry in the `UdfCostCatalog`.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    impl_file_path: str
    type: str
    row_id: int
    thorughput_cost: int = None

    def display_format(self):
        # TODO: figure out what needs to be returned in the display format
        data_type = self.type.name

        return {"name": self.name, "data_type": data_type}
