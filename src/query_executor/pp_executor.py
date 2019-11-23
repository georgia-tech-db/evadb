from typing import Iterator

from src.models.storage.batch import FrameBatch
from src.query_executor.abstract_executor import AbstractExecutor
from src.query_planner.abstract_plan import AbstractPlan
from src.query_planner.pp_plan import PPScanPlan


class PPExecutor(AbstractExecutor):
    """
      Applies PP to filter out the frames that doesn't satisfy the condition
      Arguments:
          node (AbstractPlan): ...

    Note: This look kind of redundant. This logic for now is similar to that
    of sequential scan executor. Will decide to delete it depending on how
    sequential scan evolves.
    """

    def __init__(self, node: PPScanPlan):
        super().__init__(node)
        self.predicate = node.predicate

    def validate(self):
        pass

    def next(self) -> Iterator[FrameBatch]:
        child_executor = self.children[0]
        for batch in child_executor.next():
            outcomes = self.predicate.evaluate(batch)
            required_frame_ids = []
            for i, outcome in enumerate(outcomes):
                if outcome:
                    required_frame_ids.append(i)

            yield batch[required_frame_ids]
