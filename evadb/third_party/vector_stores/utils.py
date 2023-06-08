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
from evadb.catalog.catalog_type import VectorStoreType
from evadb.third_party.vector_stores.faiss import FaissVectorStore
from evadb.third_party.vector_stores.qdrant import QdrantVectorStore
from evadb.utils.generic_utils import validate_kwargs


class VectorStoreFactory:
    @staticmethod
    def init_vector_store(
        vector_store_type: VectorStoreType, index_name: str, **kwargs
    ):
        if vector_store_type == VectorStoreType.FAISS:
            from evadb.third_party.vector_stores.faiss import required_params

            validate_kwargs(kwargs, required_params, required_params)
            return FaissVectorStore(index_name, **kwargs)

        elif vector_store_type == VectorStoreType.QDRANT:
            from evadb.third_party.vector_stores.qdrant import required_params

            validate_kwargs(kwargs, required_params, required_params)
            return QdrantVectorStore(index_name, **kwargs)

        else:
            raise Exception(f"Vector store {vector_store_type} not supported")
