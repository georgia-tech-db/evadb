from typing import Generator, Iterator

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError, apply_predicate
from eva.models.storage.batch import Batch
from eva.plan_nodes.predicate_plan import PredicatePlan
from eva.utils.logging_manager import logger


class DeleteExecutor(AbstractExecutor):
    """
    Delete Tuples
    """

    def __init__(self, node: PredicatePlan):
        super().__init__(node)
        self.predicate = node.predicate

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        try:
            print("hello, world!")
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)
