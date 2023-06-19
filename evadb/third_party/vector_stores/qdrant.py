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
from evadb.utils.generic_utils import try_to_import_qdrant_client

_qdrant_client_instance = None

required_params = ["index_db"]


def get_qdrant_client(path: str):
    global _qdrant_client_instance
    if _qdrant_client_instance is None:
        try_to_import_qdrant_client()
        import qdrant_client  # noqa: F401

        # creating a local mode client
        # modify to support server modes
        # https://github.com/qdrant/qdrant-client
        _qdrant_client_instance = qdrant_client.QdrantClient(path=path)
    return _qdrant_client_instance


class QdrantVectorStore(VectorStore):
    def __init__(self, index_name: str, index_db: str) -> None:
        self._client = get_qdrant_client(index_db)
        self._collection_name = index_name

    def create(self, vector_dim: int):
        from qdrant_client.models import Distance, VectorParams

        self._client.recreate_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
        )

    def add(self, payload: List[FeaturePayload]):
        from qdrant_client.models import Batch

        ids = [int(row.id) for row in payload]
        embeddings = [row.embedding.reshape(-1).tolist() for row in payload]
        self._client.upsert(
            collection_name=self._collection_name,
            points=Batch.construct(
                ids=ids,
                vectors=embeddings,
            ),
        )

    def delete(self) -> None:
        self._client.delete_collection(
            collection_name=self._collection_name,
        )

    def query(
        self,
        query: VectorIndexQuery,
    ) -> VectorIndexQueryResult:
        response = self._client.search(
            collection_name=self._collection_name,
            query_vector=query.embedding.reshape(-1).tolist(),
            limit=query.top_k,
        )

        distances, ids = [], []
        for point in response:
            distances.append(point.score)
            ids.append(int(point.id))

        return VectorIndexQueryResult(distances, ids)
