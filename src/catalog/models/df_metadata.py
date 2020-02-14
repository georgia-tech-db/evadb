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

from src.catalog.df_schema import DataFrameSchema
from src.catalog.models.base_model import BaseModel


class DataFrameMetadata(BaseModel):
    __tablename__ = 'df_metadata'

    _name = Column('name', String(100), unique=True)
    _file_url = Column('file_url', String(100))

    def __init__(self, name: str, file_url: str,
                 dataframe_schema: DataFrameSchema = None):
        self._name = name
        self._file_url = file_url
        if dataframe_schema is not None:
            self._dataframe_schema = dataframe_schema
            self._dataframe_petastorm_schema = \
                dataframe_schema.get_petastorm_schema()
            self._dataframe_pyspark_schema = \
                self._dataframe_petastorm_schema.as_spark_schema()

    def set_schema(self, schema):
        self._dataframe_schema = schema
        self._dataframe_petastorm_schema = \
            schema.get_petastorm_schema()
        self._dataframe_pyspark_schema = \
            self._dataframe_petastorm_schema.as_spark_schema()

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_dataframe_file_url(self):
        return self._file_url

    def get_dataframe_schema(self):
        return self._dataframe_schema

    def get_dataframe_petastorm_schema(self):
        return self._dataframe_petastorm_schema

    def get_dataframe_pyspark_schema(self):
        return self._dataframe_pyspark_schema

    @classmethod
    def create(cls, name, file_url):
        metadata = DataFrameMetadata(name=name, file_url=file_url)
        metadata = metadata.save()
        if metadata is None:
            raise Exception('Object already created.')
        return metadata

    @classmethod
    def get_id_from_name(cls, name):
        result = DataFrameMetadata.query \
            .with_entities(DataFrameMetadata._id) \
            .filter(DataFrameMetadata._name == name).one()
        return result[0]

    @classmethod
    def get(cls, metadata_id):
        result = DataFrameMetadata.query \
            .filter(DataFrameMetadata._id == metadata_id) \
            .one()
        print(result)
        return result
