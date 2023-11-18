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
from evadb.expression.abstract_expression import AbstractExpression, ExpressionType
from evadb.expression.arithmetic_expression import ArithmeticExpression
from evadb.expression.comparison_expression import ComparisonExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.logical_expression import LogicalExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
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
    Collection,
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


def etype_to_milvus_symbol(etype: ExpressionType):
    if etype == ExpressionType.COMPARE_EQUAL:
        return "=="
    elif etype == ExpressionType.COMPARE_GREATER:
        return ">"
    elif etype == ExpressionType.COMPARE_LESSER:
        return "<"
    elif etype == ExpressionType.COMPARE_GEQ:
        return ">="
    elif etype == ExpressionType.COMPARE_LEQ:
        return "<="
    elif etype == ExpressionType.COMPARE_NEQ:
        return "!="
    elif etype == ExpressionType.COMPARE_LIKE:
        return "LIKE"
    elif etype == ExpressionType.LOGICAL_AND:
        return "and"
    elif etype == ExpressionType.LOGICAL_OR:
        return "or"
    elif etype == ExpressionType.LOGICAL_NOT:
        return "not"
    elif etype == ExpressionType.ARITHMETIC_ADD:
        return "+"
    elif etype == ExpressionType.ARITHMETIC_DIVIDE:
        return "/"
    elif etype == ExpressionType.ARITHMETIC_MULTIPLY:
        return "*"
    elif etype == ExpressionType.ARITHMETIC_SUBTRACT:
        return "-"


def expression_to_milvus_expr(expr: AbstractExpression):
    if isinstance(expr, ComparisonExpression) or isinstance(expr, ArithmeticExpression):
        milvus_symbol = etype_to_milvus_symbol(expr.etype)
        return f"({expression_to_milvus_expr(expr.children[0])} {milvus_symbol} {expression_to_milvus_expr(expr.children[1])})"
    elif isinstance(expr, LogicalExpression):
        milvus_symbol = etype_to_milvus_symbol(expr.etype)
        if expr.etype == ExpressionType.LOGICAL_NOT:
            return f"({milvus_symbol} {expression_to_milvus_expr(expr.children[0])})"
        else:
            return f"({expression_to_milvus_expr(expr.children[0])} {milvus_symbol} {expression_to_milvus_expr(expr.children[1])})"
    elif isinstance(expr, ConstantValueExpression):
        return expr.value
    elif isinstance(expr, TupleValueExpression):
        return expr.name


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

    def create(
        self,
        vector_dim: int,
        metadata_column_catalog_entries: List[ColumnCatalogEntry] = None,
    ):
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

        metadata_fields = [
            FieldSchema(
                name=entry.name,
                dtype=column_type_to_milvus_type(entry.type),
            )
            for entry in metadata_column_catalog_entries
        ]

        schema = CollectionSchema(
            fields=[id_field] + [embedding_field] + metadata_fields
        )

        # Create collection
        collection = Collection(
            name=self._collection_name,
            schema=schema,
            using=self._milvus_connection_alias,
        )

        # Create index on collection
        collection.create_index(
            "vector",
            {
                "metric_type": "COSINE",
                "params": {},
            },
        )

        collection.load()

    def add(self, payload: List[FeaturePayload]):
        milvus_data = [
            {
                "id": feature_payload.id,
                "vector": feature_payload.embedding.reshape(-1).tolist(),
                **feature_payload.metadata,
            }
            for feature_payload in payload
        ]

        collection = Collection(
            name=self._collection_name, using=self._milvus_connection_alias
        )

        collection.upsert(milvus_data)

    def persist(self):
        collection = Collection(
            name=self._collection_name, using=self._milvus_connection_alias
        )

        collection.flush()

    def delete(self) -> None:
        utility.drop_collection(
            self._collection_name, using=self._milvus_connection_alias
        )

    def query(self, query: VectorIndexQuery) -> VectorIndexQueryResult:
        collection = Collection(
            name=self._collection_name, using=self._milvus_connection_alias
        )

        response = collection.search(
            data=[query.embedding.reshape(-1).tolist()],
            anns_field="vector",
            param={"metric_type": "COSINE"},
            limit=query.top_k,
            expr=expression_to_milvus_expr(query.filter_expr_str),
        )[0]

        distances, ids = response.distances, response.ids

        return VectorIndexQueryResult(distances, ids)
