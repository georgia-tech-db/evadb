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
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from eva.catalog.models.association_models import depend_udf_and_udf_cache
from eva.catalog.models.base_model import BaseModel
from eva.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from eva.catalog.models.udf_metadata_catalog import UdfMetadataCatalogEntry


class UdfCatalog(BaseModel):
    """The `UdfCatalog` catalog stores information about the user-defined functions (UDFs) in the system. It maintains the following information for each UDF
    `_row_id:` an autogenerated identifier
    `_impl_file_path: ` the path to the implementation script for the UDF
    `_type:` an optional tag associated with the UDF (useful for grouping similar UDFs, such as multiple object detection UDFs)
    """

    __tablename__ = "udf_catalog"

    _name = Column("name", String(128), unique=True)
    _impl_file_path = Column("impl_file_path", String(128))
    _type = Column("type", String(128))
    _checksum = Column("checksum", String(512))

    # UdfIOCatalog storing the input/output attributes of the udf
    _attributes = relationship(
        "UdfIOCatalog", back_populates="_udf", cascade="all, delete, delete-orphan"
    )
    _metadata = relationship(
        "UdfMetadataCatalog",
        back_populates="_udf",
        cascade="all, delete, delete-orphan",
    )

    _dep_caches = relationship(
        "UdfCacheCatalog",
        secondary=depend_udf_and_udf_cache,
        back_populates="_udf_depends",
        cascade="all, delete",
    )

    def __init__(self, name: str, impl_file_path: str, type: str, checksum: str):
        self._name = name
        self._impl_file_path = impl_file_path
        self._type = type
        self._checksum = checksum

    def as_dataclass(self) -> "UdfCatalogEntry":
        args = []
        outputs = []
        for attribute in self._attributes:
            if attribute._is_input:
                args.append(attribute.as_dataclass())
            else:
                outputs.append(attribute.as_dataclass())

        metadata = []
        for meta_key_value in self._metadata:
            metadata.append(meta_key_value.as_dataclass())

        return UdfCatalogEntry(
            row_id=self._row_id,
            name=self._name,
            impl_file_path=self._impl_file_path,
            type=self._type,
            checksum=self._checksum,
            args=args,
            outputs=outputs,
            metadata=metadata,
            dep_caches=[entry.as_dataclass() for entry in self._dep_caches],
        )


@dataclass(unsafe_hash=True)
class UdfCatalogEntry:
    """Dataclass representing an entry in the `UdfCatalog`.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    impl_file_path: str
    type: str
    checksum: str
    row_id: int = None
    args: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)
    outputs: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)
    metadata: List[UdfMetadataCatalogEntry] = field(compare=False, default_factory=list)
    dep_caches: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)

    def display_format(self):
        def _to_str(col):
            col_display = col.display_format()
            return f"{col_display['name']} {col_display['data_type']}"

        return {
            "name": self.name,
            "inputs": [_to_str(col) for col in self.args],
            "outputs": [_to_str(col) for col in self.outputs],
            "type": self.type,
            "impl": self.impl_file_path,
            "metadata": self.metadata,
        }
