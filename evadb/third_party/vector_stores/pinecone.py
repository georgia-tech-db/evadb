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

from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.third_party.vector_stores.types import (
    FeaturePayload,
    VectorIndexQuery,
    VectorIndexQueryResult,
    VectorStore,
)
from evadb.utils.generic_utils import try_to_import_pinecone_client
from evadb.utils.logging_manager import logger

required_params = []
_pinecone_init_done = False


class PineconeVectorStore(VectorStore):
    def __init__(self, index_name: str) -> None:
        try_to_import_pinecone_client()
        global _pinecone_init_done
        # pinecone only allows index names with lower alpha-numeric characters and '-'
        self._index_name = index_name.strip().lower()

        # Get the API key.
        self._api_key = ConfigurationManager().get_value(
            "third_party", "PINECONE_API_KEY"
        )

        if not self._api_key:
            self._api_key = os.environ.get("PINECONE_API_KEY")

        assert (
            self._api_key
        ), "Please set your Pinecone API key in evadb.yml file (third_party, pinecone_api_key) or environment variable (PINECONE_KEY). It can be found at Pinecone Dashboard > API Keys > Value"

        # Get the environment name.
        self._environment = ConfigurationManager().get_value(
            "third_party", "PINECONE_ENV"
        )
        if not self._environment:
            self._environment = os.environ.get("PINECONE_ENV")

        assert (
            self._environment
        ), "Please set the Pinecone environment key in evadb.yml file (third_party, pinecone_env) or environment variable (PINECONE_ENV). It can be found Pinecone Dashboard > API Keys > Environment."

        if not _pinecone_init_done:
            # Initialize pinecone.
            import pinecone

            pinecone.init(api_key=self._api_key, environment=self._environment)
            _pinecone_init_done = True
        self._client = None

    def create(self, vector_dim: int):
        import pinecone

        pinecone.create_index(self._index_name, dimension=vector_dim, metric="cosine")
        logger.warning(
            f"""Created index {self._index_name}. Please note that Pinecone is eventually consistent, hence any additions to the Vector Index may not get immediately reflected in queries."""
        )
        self._client = pinecone.Index(self._index_name)

    def add(self, payload: List[FeaturePayload]):
        self._client.upsert(
            vectors=[
                {"id": str(row.id), "values": row.embedding.reshape(-1).tolist()}
                for row in payload
            ]
        )

    def delete(self) -> None:
        import pinecone

        pinecone.delete_index(self._index_name)

    def query(
        self,
        query: VectorIndexQuery,
    ) -> VectorIndexQueryResult:
        import pinecone

        if not self._client:
            self._client = pinecone.Index(self._index_name)

        response = self._client.query(
            top_k=query.top_k, vector=query.embedding.reshape(-1).tolist()
        )

        distances, ids = [], []

        for row in response["matches"]:
            distances.append(row["score"])
            ids.append(int(row["id"]))

        return VectorIndexQueryResult(distances, ids)
