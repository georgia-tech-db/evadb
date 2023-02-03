from typing import Generator, Iterator

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, apply_predicate
from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.plan_nodes.project_plan import ProjectPlan
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
            child_executor = self.children[0]
            for batch in child_executor.exec(*args, **kwargs):
                batch = apply_predicate(batch, self.predicate)
                if not batch.empty():
                    yield batch
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)

    def __call__(self, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec(**kwargs)
