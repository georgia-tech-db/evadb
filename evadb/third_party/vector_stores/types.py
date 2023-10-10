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
from dataclasses import dataclass
from typing import List
from uuid import uuid5, NAMESPACE_DNS


@dataclass
class FeaturePayload:
    id: int
    embedding: List[float]


@dataclass
class VectorIndexQuery:
    embedding: List[float]
    top_k: int


@dataclass
class VectorIndexQueryResult:
    similarities: List[float]
    ids: List[int]

class VectorStore:
    def create(self, vector_dim: int):
        """Create an index"""
        ...

    def add(self, payload: List[FeaturePayload]) -> None:
        """Add embeddings to the vector store"""
        ...

    def persist(self) -> None:
        """Persist index to disk"""
        return None

    def query(self, query: VectorIndexQuery) -> VectorIndexQueryResult:
        """Query index"""
        ...

    def delete(self):
        """delete an index"""
        ...

    def create_weaviate_class(self, class_name: str, vectorizer: str, module_config: dict, properties: list) -> None:
        """
         Create a Weaviate class with the specified configuration.

         Args:
             class_name (str): The name of the class to create, e.g., "Article".
             vectorizer (str): The vectorizer module to use, e.g., "text2vec-cohere".
             module_config (dict): Configuration for vectorizer and generative module, e.g.,
                 {
                     "text2vec-cohere": {
                         "model": "embed-multilingual-v2.0",
                     },
                 }
             properties (list): List of dictionaries specifying class properties, e.g.,
                 [
                     {
                         "name": "title",
                         "dataType": ["text"]
                     },
                     {
                         "name": "body",
                         "dataType": ["text"]
                     },
                 ]

         Returns:
             None
         """
        # Implement the logic to create a Weaviate class with the given parameters.
        ...

    def delete_weaviate_class(self, class_name: str) -> None:
        """
        Delete a Weaviate class and its data.

        Args:
            class_name (str): The name of the Weaviate class to delete.

        Returns:
            None
        """
        # Implement the logic to delete a Weaviate class and its data.
        ...

    def add_to_weaviate_class(self, class_name: str, data_objects: List[dict]) -> None:
        """
        Add objects to the specified Weaviate class.

        Args:
            class_name (str): The name of the Weaviate class to add objects to.
            data_objects (List[dict]): A list of dictionaries, where each dictionary contains property names and values.

        Returns:
            None
        """
        # Implement the logic to add payloads to a Weaviate class.
        ...

    def query_weaviate_class(self, class_name, properties_to_retrieve, query: VectorIndexQuery) -> List[dict]:
        """
        Perform a similarity-based search in Weaviate.

        Args:
            class_name (str): The name of the Weaviate class to perform the search on.
            properties_to_retrieve (List[str]): A list of property names to retrieve.
            query (VectorIndexQuery): A query object for similarity search, containing the query vector and top_k.

        Returns:
            List[dict]: A list of dictionaries containing the retrieved properties.
        """
        # Implement the logic to query a Weaviate class for similar vectors.
        ...