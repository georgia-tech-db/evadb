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

from src.catalog.models.base_model import BaseModel


class UdfMetadata(BaseModel):
    __tablename__ = 'udf'

    _name = Column('name', String(100), unique=True)
    _impl_file_path = Column('impl_file_path', String(128))
    _type = Column('type', String(100))

    _cols = relationship('UdfIO',
                         back_populates="_udf",
                         cascade='all, delete, delete-orphan')

    _metrics = relationship('UdfMetrics',
                            back_populates="_udf",
                            cascade='all, delete, delete-orphan')

    def __init__(self, name: str, impl_file_path: str, type: str):
        self._name = name
        self._impl_file_path = impl_file_path
        self._type = type

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def impl_file_path(self):
        return self._impl_file_path

    @property
    def type(self):
        return self._type

    def __str__(self):
        udf_str = 'udf: ({}, {}, {})\n'.format(
            self.name, self.impl_file_path, self.type)
        return udf_str

    def __eq__(self, other):
        return self.id == other.id and \
            self.impl_file_path == other.impl_file_path and \
            self.name == other.name and \
            self.type == other.type
