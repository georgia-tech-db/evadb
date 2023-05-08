from eva.catalog.catalog_type import IndexType
from eva.third_party.vector_stores.faiss import FaissVectorStore


class VectorStoreFactory:
    @staticmethod
    def create_vector_store(index_type: IndexType, name: str, input_dim: int):
        if index_type == IndexType.FAISS:
            return FaissVectorStore(name, input_dim)
