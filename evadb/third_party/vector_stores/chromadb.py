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
from typing import List

from evadb.third_party.vector_stores.types import (
    FeaturePayload,
    VectorIndexQuery,
    VectorIndexQueryResult,
    VectorStore,
)
from evadb.utils.generic_utils import try_to_import_chromadb_client

_chromadb_client_instance = None

required_params = ["index_path"]


def get_chromadb_client(index_path: str):
    global _chromadb_client_instance
    if _chromadb_client_instance is None:
        try_to_import_chromadb_client()
        import chromadb  # noqa: F401

        # creating a local client
        _chromadb_client_instance = chromadb.PersistentClient(path=index_path)
    return _chromadb_client_instance


class ChromaDBVectorStore(VectorStore):
    def __init__(self, index_name: str, index_path: str) -> None:
        self._client = get_chromadb_client(index_path)
        self._collection_name = index_name

    def create(self, vector_dim: int):
        self._client.create_collection(
            name=self._collection_name,
            metadata={"hnsw:construction_ef": vector_dim, "hnsw:space": "cosine"},
        )

    def add(self, payload: List[FeaturePayload]):
        ids = [str(row.id) for row in payload]
        embeddings = [row.embedding.reshape(-1).tolist() for row in payload]
        self._client.get_collection(self._collection_name).add(
            ids=ids,
            embeddings=embeddings,
        )

    def delete(self) -> None:
        self._client.delete_collection(
            name=self._collection_name,
        )

    def query(
        self,
        query: VectorIndexQuery,
    ) -> VectorIndexQueryResult:
        response = self._client.get_collection(self._collection_name).query(
            query_embeddings=query.embedding.reshape(-1).tolist(),
            n_results=query.top_k,
        )

        distances, ids = [], []
        if "ids" in response:
            for id in response["ids"][0]:
                ids.append(int(id))
            for distance in response["distances"][0]:
                distances.append(distance)

        return VectorIndexQueryResult(distances, ids)
