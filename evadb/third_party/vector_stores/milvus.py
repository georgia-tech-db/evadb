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
import atexit
from typing import List

from evadb.third_party.vector_stores.types import (
    FeaturePayload,
    VectorIndexQuery,
    VectorIndexQueryResult,
    VectorStore,
)
from evadb.utils.generic_utils import try_to_import_milvus_client

_milvus_client_instance = None
_milvus_server_instance = None

required_params = ["index_dir"]


def get_local_milvus_server(index_dir: str):
    global _milvus_server_instance
    if _milvus_server_instance is None:
        try_to_import_milvus_client()
        import milvus

        _milvus_server_instance = milvus.default_server
        _milvus_server_instance.set_base_dir(index_dir)
        _milvus_server_instance.start()

        # Ensure that local Milvus server is terminated before Python process terminates
        atexit.register(_milvus_server_instance.stop)
    return _milvus_server_instance


def get_milvus_client(server_address: str, server_port: int):
    global _milvus_client_instance
    if _milvus_client_instance is None:
        try_to_import_milvus_client()
        import pymilvus

        server_uri = f"http://{server_address}:{server_port}"
        _milvus_client_instance = pymilvus.MilvusClient(uri=server_uri)

    return _milvus_client_instance


class MilvusVectorStore(VectorStore):
    def __init__(self, index_name: str, index_dir: str) -> None:
        local_milvus_server = get_local_milvus_server(index_dir)
        self._client = get_milvus_client(
            server_address=local_milvus_server.server_address,
            server_port=local_milvus_server.listen_port,
        )
        self._collection_name = index_name

    def create(self, vector_dim: int):
        if self._collection_name in self._client.list_collections():
            self._client.drop_collection(self._collection_name)
        self._client.create_collection(
            collection_name=self._collection_name, dimension=vector_dim
        )

    def add(self, payload: List[FeaturePayload]):
        milvus_data = [
            {
                "id": feature_payload.id,
                "vector": feature_payload.embedding.reshape(-1).tolist(),
            }
            for feature_payload in payload
        ]
        ids = [feature_payload.id for feature_payload in payload]

        # Milvus Client does not have upsert operation, perform delete + insert to emulate it
        self._client.delete(collection_name=self._collection_name, pks=ids)

        self._client.insert(collection_name=self._collection_name, data=milvus_data)

    def persist(self):
        self._client.flush(self._collection_name)

    def delete(self) -> None:
        self._client.drop_collection(
            collection_name=self._collection_name,
        )

    def query(self, query: VectorIndexQuery) -> VectorIndexQueryResult:
        response = self._client.search(
            collection_name=self._collection_name,
            data=[query.embedding.reshape(-1).tolist()],
            limit=query.top_k,
        )[0]

        distances, ids = [], []
        for result in response:
            print(result)
            distances.append(result["distance"])
            ids.append(result["id"])

        return VectorIndexQueryResult(distances, ids)
