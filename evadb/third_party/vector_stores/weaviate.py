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
    VectorStore,
)
from evadb.utils.generic_utils import try_to_import_weaviate_client

required_params = []
_weaviate_init_done = False


class WeaviateVectorStore(VectorStore):
    def __init__(self) -> None:
        try_to_import_weaviate_client()
        global _weaviate_init_done

        # Get the API key.
        self._api_key = ConfigurationManager().get_value(
            "third_party", "WEAVIATE_API_KEY"
        )

        if not self._api_key:
            self._api_key = os.environ.get("WEAVIATE_API_KEY")


        assert (
            self._api_key
        ), "Please set your Weaviate API key in evadb.yml file (third_party, weaviate_api_key) or environment variable (WEAVIATE_API_KEY). It can be found at the Details tab in WCS Dashboard."

        # Get the API Url.
        self._api_url = ConfigurationManager().get_value(
            "third_party", "WEAVIATE_API_URL"
        )

        if not self._api_url:
            self._api_url = os.environ.get("WEAVIATE_API_URL")

        assert (
            self._api_url
        ), "Please set your Weaviate API Url in evadb.yml file (third_party, weaviate_api_url) or environment variable (WEAVIATE_API_URL). It can be found at the Details tab in WCS Dashboard."


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

    def create_weaviate_class(self, class_name: str, vectorizer: str, module_config: dict, properties: list) -> None:
        # In Weaviate, vector index creation and management is not explicitly done like Pinecone
        # Need to typically define a property in the schema to hold vectors and insert data accordingly

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
        # Check if the class already exists
        if self._client.schema.exists(class_name):
            self._client.schema.delete_class(class_name)

        # Define the class object with provided parameters
        class_obj = {
            "class": class_name,
            "vectorizer": vectorizer,
            "moduleConfig": module_config,
            "properties": properties
        }


        # Call the Weaviate API to create the class
        self._client.schema.create_class(class_obj)

        # response = client.schema.get(class_name)
        # Check the response for success or handle any errors
        if self._client.schema.get(class_name)['class'] == class_name:
            print(f"Successfully created Weaviate class '{class_name}'")
        else:
            print(f"Failed to create Weaviate class '{class_name}'")

        return None

    def delete_weaviate_class(self, class_name: str) -> None:
        """
        Delete a Weaviate class and its data.

        Args:
            class_name (str): The name of the Weaviate class to delete.

        Returns:
            None
        """
        # Call the Weaviate API to delete the class
        self._client.schema.delete_class(class_name)

        try:
            # Attempt to retrieve the class, and if it results in an exception,
            # consider the class as successfully deleted.
            self._client.schema.get(class_name)
            print(f"Failed to delete Weaviate class '{class_name}'")
        except Exception as e:
            print(f"Successfully deleted Weaviate class '{class_name}'")

        return None

    def add_to_weaviate_class(self, class_name: str, data_objects: List[dict]) -> None:
        """
        Add objects to the specified Weaviate class.

        Args:
            class_name (str): The name of the Weaviate class to add objects to.
            data_objects (List[dict]): A list of dictionaries, where each dictionary contains property names and values.

        Returns:
            None
        """
        # Iterate over each data object and add it to the Weaviate class
        for data_object in data_objects:
            self._client.data_object.create(data_object, class_name)

        return None

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
        try:
            # Define the similarity search query
            response = (
                self._client.query
                .get(class_name, properties_to_retrieve)
                .with_near_vector({
                    "vector": query.embedding
                })
                .with_limit(query.top_k)
                .with_additional(["distance"])
                .do()
            )

            # Check if the response contains data
            data = response.get('data', {})
            if 'Get' not in data or class_name not in data['Get']:
                print(f"No objects of class {class_name} found.")
                return []

            # Extract the results
            results = data['Get'][class_name]

            return results

        except Exception as e:
            print(f"Failed to query Weaviate class '{class_name}'")
            print(e)

            return []