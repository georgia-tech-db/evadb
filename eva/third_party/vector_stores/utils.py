from eva.catalog.catalog_type import IndexType
from eva.third_party.vector_stores.faiss import FaissVectorStore


class VectorStoreFactory:
    @staticmethod
    def get_vector_store_client(index_type: IndexType, name: str, input_dim: int):
        if index_type == IndexType.FAISS:
            return FaissVectorStore()

    @staticmethod
    def get_vector_index(index_type: IndexType, name: str, index_path: str = None):
        if index_type == IndexType.FAISS:
            return FaissVectorStore(name, input_dim)
