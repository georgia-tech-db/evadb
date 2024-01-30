from typing import List

from evadb.third_party.vector_stores.types import (
    FeaturePayload,
    VectorIndexQuery,
    VectorIndexQueryResult,
    VectorStore,
)
from evadb.utils.generic_utils import try_to_import_marqo_client

_marqo_client_instance = None

required_params = ["url", "index_name"]


def get_marqo_client(url: str, api_key: str=None):
    global _marqo_client_instance
    if _marqo_client_instance is None:
        try_to_import_marqo_client()
        import marqo as  mq
        _marqo_client_instance = mq.Client(url=url, api_key=api_key)
    return _marqo_client_instance


class MarqoVectorStore(VectorStore):
    def __init__(self, index_name: str, url: str = "http://0.0.0.0:8882", api_key=None) -> None:
        self._client = get_marqo_client(url=url)
        self._index_name = index_name

    def create(self, vector_dim: int):

        # Delete index if exists already
        if self._index_name in [i.index_name for i in self._client.get_indexes()['results']]:
            self.delete()

        # create fresh
        # Refer here for details - https://docs.marqo.ai/2.0.0/API-Reference/Indexes/create_index/
        self._client.create_index(
            index_name=self._index_name,
            settings_dict={
                'index_defaults': {
                    'model': 'no_model',
                    'model_properties': {
                        'dimensions': vector_dim
                    },

                    'normalize_embeddings': True,
                    'ann_parameters':{
                        'space_type': 'cosinesimil'
                    }
                }
            }
        )

    def add(self, payload: List[FeaturePayload]):

        ids = [int(row.id) for row in payload]
        embeddings = [row.embedding for row in payload]
        
        data = []
        for _id, _emb in zip(ids, embeddings):
            _id = str(_id)
            data.append(
                {
                    '_id': _id,
                    'evadb_data':{
                        'vector': _emb
                    }
                }
            )
        
        # For reference and more information
        # check - https://docs.marqo.ai/1.4.0/Guides/Advanced-Usage/document_fields/#custom-vector-object
        self._client.index(
            index_name=self._index_name
            ).add_documents(
            documents=data,
            mappings={
                'evadb_data':{
                'type': 'custom_vector'
                }
            },
            tensor_fields=['evadb_data'],
            auto_refresh=True,
            client_batch_size=64
            )
        

    def delete(self) -> None:
        self._client.delete_index(index_name=self._index_name)

    def query(
        self,
        query: VectorIndexQuery,
    ) -> VectorIndexQueryResult:
        response = self._client.index(
            self._index_name).search(
                context={
                    'tensor':[
                        {
                            'vector': list(query.embedding), 
                            'weight' : 1
                        }
                        ],
                        }, 
                limit=query.top_k
            )

        similarities, ids = [], []

        for result in response['hits']:
            ids.append(result['_id'])

            # Because it is similarity score
            similarities.append(1-result['_score']) 

        return VectorIndexQueryResult(similarities=similarities, ids=ids)

