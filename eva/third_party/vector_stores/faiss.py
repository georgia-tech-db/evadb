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

import numpy as np

from eva.third_party.vector_stores.types import FeaturePayload, VectorStore

_faiss = None


def _lazy_load_faiss():
    global _faiss
    if _faiss is None:
        import_err_msg = "`faiss` package not found, please visit https://github.com/facebookresearch/faiss/wiki/Installing-Faiss for instructions"
        try:
            import faiss  # noqa: F401

            _faiss = faiss
        except ImportError:
            raise ImportError(import_err_msg)
    return _faiss


class FaissVectorStore(VectorStore):
    def __init__(self, index_name: str, vector_dim: int) -> None:
        # Refernce to Faiss documentation.
        # IDMap: https://github.com/facebookresearch/faiss/wiki/Pre--and-post-processing#faiss-id-mapping
        # Other index types: https://github.com/facebookresearch/faiss/wiki/The-index-factory
        faiss = _lazy_load_faiss()
        self._index = faiss.IndexIDMap2(faiss.IndexHNSWFlat(vector_dim, 32))
        self._index_name = index_name

    def add(self, payload: List[FeaturePayload]):
        for row in payload:
            embedding = np.array(row.embedding, dtype="float32")
            if len(embedding.shape) != 2:
                embedding = embedding.reshape(1, -1)
            self._index.add_with_ids(embedding, np.array([row.id]))

    def persist(self, path: str):
        faiss = _lazy_load_faiss()
        faiss.write_index(self._index, path)
