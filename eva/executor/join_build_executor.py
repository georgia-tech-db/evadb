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
        # build in memory hash table and pass to the probe phase
        # Assumption the hash table fits in memory 
        # Todo: Implement a partition based hash join (grace hash join)
        cumm_batches = []
        for batch in child_executor.exec():
            if not batch.empty():
                cumm_batches.append(batch)
        cumm_batches = Batch.concat(cumm_batches)
        cumm_batches.frames.index = cumm_batches.frames[self.join_keys].apply(lambda x: hash(tuple(x)), axis=1)
        yield cumm_batches
