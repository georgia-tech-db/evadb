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
import os
from typing import List

from evadb.third_party.vector_stores.types import (
    FeaturePayload,
    VectorIndexQuery,
    VectorIndexQueryResult,
    VectorStore,
)
from evadb.utils.generic_utils import try_to_import_weaviate_client

required_params = []
_weaviate_init_done = False


class WeaviateVectorStore(VectorStore):
    def __init__(self, collection_name: str, **kwargs) -> None:
        try_to_import_weaviate_client()
        global _weaviate_init_done

        self._collection_name = collection_name

        # Get the API key.
        self._api_key = kwargs.get("WEAVIATE_API_KEY")

        if not self._api_key:
            self._api_key = os.environ.get("WEAVIATE_API_KEY")

        assert (
            self._api_key
        ), "Please set your `WEAVIATE_API_KEY` using set command or environment variable (WEAVIATE_API_KEY). It can be found at the Details tab in WCS Dashboard."

        # Get the API Url.
        self._api_url = kwargs.get("WEAVIATE_API_URL")

        if not self._api_url:
            self._api_url = os.environ.get("WEAVIATE_API_URL")

        assert (
            self._api_url
        ), "Please set your `WEAVIATE_API_URL` using set command or environment variable (WEAVIATE_API_URL). It can be found at the Details tab in WCS Dashboard."

        if not _weaviate_init_done:
            # Initialize weaviate client
            import weaviate

            client = weaviate.Client(
                url=self._api_url,
                auth_client_secret=weaviate.AuthApiKey(api_key=self._api_key),
            )
            client.schema.get()

            _weaviate_init_done = True

        self._client = client

    def create(
        self,
        vectorizer: str = "text2vec-openai",
        properties: list = None,
        module_config: dict = None,
    ):
        properties = properties or []
        module_config = module_config or {}

        collection_obj = {
            "class": self._collection_name,
            "properties": properties,
            "vectorizer": vectorizer,
            "moduleConfig": module_config,
        }

        if self._client.schema.exists(self._collection_name):
            self._client.schema.delete_class(self._collection_name)

        self._client.schema.create_class(collection_obj)

    def add(self, payload: List[FeaturePayload]) -> None:
        with self._client.batch as batch:
            for item in payload:
                data_object = {"id": item.id, "vector": item.embedding}
                batch.add_data_object(data_object, self._collection_name)

    def delete(self) -> None:
        self._client.schema.delete_class(self._collection_name)

    def query(self, query: VectorIndexQuery) -> VectorIndexQueryResult:
        response = (
            self._client.query.get(self._collection_name, ["*"])
            .with_near_vector({"vector": query.embedding})
            .with_limit(query.top_k)
            .do()
        )

        data = response.get("data", {})
        results = data.get("Get", {}).get(self._collection_name, [])

        similarities = [item["_additional"]["distance"] for item in results]
        ids = [item["id"] for item in results]

        return VectorIndexQueryResult(similarities, ids)
