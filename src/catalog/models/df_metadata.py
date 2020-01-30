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
from sqlalchemy import Column, String, Integer

from src.catalog.database import BaseModel


class DataFrameMetadata(BaseModel):
    __tablename__ = 'df_metadata'

    _id = Column('id', Integer, primary_key=True)
    _name = Column('name', String)
    _file_url = Column('file_url', String)

    def __init__(self, dataframe_file_url, dataframe_schema):
        self._file_url = dataframe_file_url
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

    def get_dataframe_file_url(self):
        return self._file_url

    def get_dataframe_schema(self):
        return self._dataframe_schema

    def get_dataframe_petastorm_schema(self):
        return self._dataframe_petastorm_schema

    def get_dataframe_pyspark_schema(self):
        return self._dataframe_pyspark_schema

    @classmethod
    def get_id_from_name(cls, name):
        result = DataFrameMetadata.query \
            .with_entities(DataFrameMetadata._id) \
            .filter(DataFrameMetadata._name == name).one()
        return result

    @classmethod
    def get(cls, metadata_id):
        result = DataFrameMetadata.query \
            .with_entities(DataFrameMetadata._id) \
            .filter(DataFrameMetadata._id == metadata_id) \
            .one()
        return result
