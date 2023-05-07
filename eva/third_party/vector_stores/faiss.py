from typing import List

import numpy as np
from eva.third_party.vector_stores.types import FeaturePayload

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


class FaissVectorStore:
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
