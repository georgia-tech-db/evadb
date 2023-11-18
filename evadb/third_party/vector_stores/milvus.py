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
from typing import Dict, List

from evadb.catalog.catalog_type import ColumnType
from evadb.catalog.models.utils import ColumnCatalogEntry
from evadb.third_party.vector_stores.types import (
    FeaturePayload,
    VectorIndexQuery,
    VectorIndexQueryResult,
    VectorStore,
)
from evadb.utils.generic_utils import try_to_import_milvus_client
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection
)

allowed_params = [
    "MILVUS_URI",
    "MILVUS_USER",
    "MILVUS_PASSWORD",
    "MILVUS_DB_NAME",
    "MILVUS_TOKEN",
]
required_params = []


def column_type_to_milvus_type(column_type: ColumnType):
    if column_type == ColumnType.BOOLEAN:
        return DataType.BOOL
    elif column_type == ColumnType.INTEGER:
        return DataType.INT64
    elif column_type == ColumnType.FLOAT:
        return DataType.FLOAT
    elif column_type == ColumnType.TEXT:
        return DataType.VARCHAR
    elif column_type == ColumnType.NDARRAY:
        return DataType.FLOAT_VECTOR


def try_to_connect_to_milvus(
    milvus_uri: str,
    milvus_user: str,
    milvus_password: str,
    milvus_db_name: str,
    milvus_token: str,
):
    global _milvus_client_instance
    if _milvus_client_instance is None:
        try_to_import_milvus_client()
        import pymilvus

        _milvus_client_instance = pymilvus.MilvusClient(
            uri=milvus_uri,
            user=milvus_user,
            password=milvus_password,
            db_name=milvus_db_name,
            token=milvus_token,
        )

    return _milvus_client_instance


class MilvusVectorStore(VectorStore):
    def __init__(self, index_name: str, **kwargs) -> None:
        # Milvus URI is the only required
        self._milvus_uri = kwargs.get("MILVUS_URI")

        if not self._milvus_uri:
            self._milvus_uri = os.environ.get("MILVUS_URI")

        assert (
            self._milvus_uri
        ), "Please set your Milvus URI in evadb.yml file (third_party, MILVUS_URI) or environment variable (MILVUS_URI)."

        # Check other Milvus variables for additional customization
        self._milvus_user = kwargs.get("MILVUS_USER")

        if not self._milvus_user:
            self._milvus_user = os.environ.get("MILVUS_USER", "")

        self._milvus_password = kwargs.get("MILVUS_PASSWORD")

        if not self._milvus_password:
            self._milvus_password = os.environ.get("MILVUS_PASSWORD", "")

        self._milvus_db_name = kwargs.get("MILVUS_DB_NAME")

        if not self._milvus_db_name:
            self._milvus_db_name = os.environ.get("MILVUS_DB_NAME", "")

        self._milvus_token = kwargs.get("MILVUS_TOKEN")

        if not self._milvus_token:
            self._milvus_token = os.environ.get("MILVUS_TOKEN", "")

        self._milvus_connection_alias = "evadb-milvus"

        connections.connect(
            self._milvus_connection_alias,
            user=self._milvus_user,
            password=self._milvus_password,
            db_name=self._milvus_db_name,
            token=self._milvus_token,
            uri=self._milvus_uri,
        )

        self._collection_name = index_name

    def create(self, vector_dim: int, metadata_column_catalog_entries: List[ColumnCatalogEntry] = None):
        # Check if collection always exists
        if utility.has_collection(
            self._collection_name, using=self._milvus_connection_alias
        ):
            utility.drop_collection(
                self._collection_name, using=self._milvus_connection_alias
            )

        # Set the collection schema for vector embedding and metadata
        embedding_field = FieldSchema(
            name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim
        )

        id_field = FieldSchema(
            name="id", dtype=DataType.INT64, is_primary=True, auto_id=False
        )

        metadata_fields = [FieldSchema(
            name=entry.name,
            dtype=column_type_to_milvus_type(entry.type),
    
        ) for entry in metadata_column_catalog_entries]

        schema = CollectionSchema(fields=[id_field] + [embedding_field] + metadata_fields)
            
        # Create collection
        collection = Collection(name=self._collection_name, schema=schema, using=self._milvus_connection_alias)

        # Create index on collection
        collection.create_index("vector", {
            "metric_type": "COSINE",
            "params": {},
        })

    def add(self, payload: List[FeaturePayload]):
        milvus_data = [
            {
                "id": feature_payload.id,
                "vector": feature_payload.embedding.reshape(-1).tolist(),
                **feature_payload.metadata
            }
            for feature_payload in payload
        ]

        collection = Collection(name=self._collection_name, using=self._milvus_connection_alias)

        collection.upsert(milvus_data)
        

    def persist(self):
        collection = Collection(name=self._collection_name, using=self._milvus_connection_alias)

        collection.flush()

    def delete(self) -> None:
        utility.drop_collection(
            self._collection_name, using=self._milvus_connection_alias
        )

    def query(self, query: VectorIndexQuery) -> VectorIndexQueryResult:
        collection = Collection(name=self._collection_name, using=self._milvus_connection_alias)

        response = collection.search(
            data=[query.embedding.reshape(-1).tolist()],
            anns_field="vector",
            param={"metric_type": "COSINE"},
            limit=query.top_k
        )[0]

        distances, ids = [], []
        for result in response:
            distances.append(result["distance"])
            ids.append(result["id"])

        return VectorIndexQueryResult(distances, ids)
