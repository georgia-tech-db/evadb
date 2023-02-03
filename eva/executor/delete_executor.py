from typing import Generator, Iterator

from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, apply_predicate
from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.plan_nodes.project_plan import ProjectPlan
from eva.storage.storage_engine import StorageEngine
from eva.utils.logging_manager import logger


class DeleteExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ProjectPlan):
        super().__init__(node)
        self.predicate = node.where_clause
        self.catalog = CatalogManager()

    def validate(self):
        pass

    def exec(self, **kwargs) -> Iterator[Batch]:
        # Uses Where clause
        try:
            storage_engine = StorageEngine.factory(self.node.table)

            if self.node.table.table_type == TableType.VIDEO_DATA:
                return storage_engine.read(
                    self.node.table,
                    self.node.batch_mem_size,
                    predicate=self.node.predicate,
                    sampling_rate=self.node.sampling_rate,
                )
            elif self.node.table.table_type == TableType.IMAGE_DATA:
                return storage_engine.read(self.node.table)
            elif self.node.table.table_type == TableType.STRUCTURED_DATA:
                return storage_engine.read(self.node.table, self.node.batch_mem_size)
            else:
                raise ExecutorError(
                    f"Unsupported TableType  {self.node.table.table_type} encountered"
                )
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)

    def __call__(self, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec(**kwargs)
