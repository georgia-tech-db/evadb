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
from typing import List

from eva.third_party.vector_stores.types import FeaturePayload

_qdrant_client_instance = None


def get_qdrant_client():
    global _qdrant_client_instance
    if _qdrant_client_instance is None:
        import_err_msg = (
            "`qdrant-client` package not found, please run `pip install qdrant-client`"
        )
        try:
            import qdrant_client  # noqa: F401
        except ImportError:
            raise ImportError(import_err_msg)

        # creating a local mode client
        # modify to support server modes
        # https://github.com/qdrant/qdrant-client
        _qdrant_client_instance = qdrant_client.QdrantClient(path="")
    return _qdrant_client_instance


class QdrantVectorStore:
    def __init__(
        self,
        index_name: str,
    ) -> None:
        self._client = get_qdrant_client()
        self._index_name = index_name

    def create(self, vector_dim: int):
        from qdrant_client.models import Distance, VectorParams

        self._client.recreate_collection(
            collection_name=self._index_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
        )

    def add(self, payload: List[FeaturePayload]):
        from qdrant_client.models import Batch

        ids = [row.id for row in payload]
        embeddings = [row.embedding for row in payload]
        self._client.upsert(
            collection_name=self._index_name,
            points=Batch.construct(
                ids=ids,
                vectors=embeddings,
            ),
        )
