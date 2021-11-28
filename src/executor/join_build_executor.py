from typing import Iterator

from src.models.storage.batch import Batch

from src.executor.abstract_executor import AbstractExecutor
from src.planner.hash_join_build_plan import HashJoinBuildPlan


class BuildJoinExecutor(AbstractExecutor):
    def __init__(self, node: HashJoinBuildPlan):
        super().__init__(node)
        self.predicate = node.join_predicate
        self.join_type = node.join_type
    def validate(self):
        pass
    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        return []