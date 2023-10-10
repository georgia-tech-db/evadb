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

from sqlalchemy import Column, String

from evadb.catalog.models.base_model import BaseModel
from evadb.catalog.models.utils import ConfigurationCatalogEntry, TextPickleType


class ConfigurationCatalog(BaseModel):
    """The `ConfigurationCatalog` catalog stores all the configuration params.
    `_row_id:` an autogenerated unique identifier.
    `_key:` the key for the config.
    `_value:` the value for the config
    """

    __tablename__ = "configuation_catalog"

    _key = Column("name", String(100), unique=True)
    _value = Column("engine", TextPickleType()) # TODO :- Will this work or would we need to pickle ??

    def __init__(self, key: str, value: any):
        self._key = key
        self._value = value

    def as_dataclass(self) -> "ConfigurationCatalogEntry":
        return ConfigurationCatalogEntry(
            row_id=self._row_id,
            key=self._key,
            value=self._value,
        )