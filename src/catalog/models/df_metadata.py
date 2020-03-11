# coding=utf-8
# Copyright 2018-2020 EVA
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
from sqlalchemy.orm import relationship

from src.catalog.df_schema import DataFrameSchema
from src.catalog.models.base_model import BaseModel


class DataFrameMetadata(BaseModel):
    __tablename__ = 'df_metadata'

    _name = Column('name', String(100), unique=True)
    _file_url = Column('file_url', String(100))

    _columns = relationship('DataFrameColumn',
                            back_populates="_dataset")

    def __init__(self, name: str, file_url: str):
        self._name = name
        self._file_url = file_url
        self._schema = None

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, column_list):
        self._schema = DataFrameSchema(self._name, column_list)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def file_url(self):
        return self._file_url

    @property
    def columns(self):
        return self._columns
