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
from sqlalchemy import null
from sqlalchemy.orm.exc import NoResultFound
from eva.catalog.column_type import IndexMethod, FaissIndexType

from eva.catalog.models.df_index import DataFrameIndex
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class IndexService(BaseService):
    def __init__(self):
        super().__init__(DataFrameIndex)

    def create_index(self,
        idx_name: str,
        faiss_idx_type: FaissIndexType,
        idx_method: IndexMethod,
        is_faiss_idx: bool,
        is_res_cache: bool,
        res_cache_path: str,
        faiss_idx_path: str,
        udf_name: str,
        metadata_id: int) -> DataFrameIndex:

        data = self.model(idx_name, faiss_idx_type, idx_method, is_faiss_idx,
                            is_res_cache, res_cache_path, faiss_idx_path, metadata_id, udf_name)
        data = data.save()
        return data

    def get_index(self, table_idx: int, udf_name: str, index_type: FaissIndexType):
        try:
            return self.model.query.filter(
                    self.model._metadata_id == table_idx,
                    self.model._udf_name == udf_name,
                    self.model._faiss_idx_type == index_type
                    ).one()
        except Exception as e:
            return None

    def get_all_index(self, table_idx: int, udf_name: str):
        try:
            return self.model.query.filter(
                    self.model._metadata_id == table_idx,
                    self.model._udf_name == udf_name,
                    self.model._is_faiss_idx == True,
                    self.model._faiss_idx_type is not None
                    ).all()
        except Exception as e:
            return None

    def get_res_cache(self, table_idx: int, udf_name: str):
        try:
            return self.model.query.filter(
                    self.model._metadata_id == table_idx,
                    self.model._udf_name == udf_name,
                    self.model._is_res_cache == True
                    ).one()
        except Exception as e:
            return None