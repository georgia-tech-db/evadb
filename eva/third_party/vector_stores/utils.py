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
from eva.catalog.catalog_type import IndexType
from eva.third_party.vector_stores.faiss import FaissVectorStore
from eva.utils.generic_utils import validate_kwargs


class VectorStoreFactory:
    @staticmethod
    def init_vector_store(index_type: IndexType, index_name: str, **kwargs):
        if index_type == IndexType.FAISS:
            from eva.third_party.vector_stores.faiss import required_params

            validate_kwargs(kwargs, required_params, required_params)
            return FaissVectorStore(index_name, **kwargs)
