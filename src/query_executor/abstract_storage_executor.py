from abc import ABC

from src.query_executor.abstract_executor import AbstractExecutor
from src.query_planner.storage_plan import StoragePlan


class AbstractStorageExecutor(AbstractExecutor, ABC):
    """
    Abstract executor for storage. This executor returns the batch frames
    from the storage layer.
    """

    def __init__(self, node: StoragePlan):
        super().__init__(node)
