from typing import Iterator

from eva.models.storage.batch import Batch

from eva.executor.abstract_executor import AbstractExecutor
from eva.planner.hash_join_build_plan import HashJoinBuildPlan


class BuildJoinExecutor(AbstractExecutor):
    def __init__(self, node: HashJoinBuildPlan):
        super().__init__(node)
        self.predicate = node.join_predicate
        self.join_type = node.join_type
    def validate(self):
        pass
    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec():

            if not batch.empty():
                yield batch