from typing import Iterator

from src.models import FrameBatch
from src.query_executor.abstract_executor import AbstractExecutor


class SequentialScanExecutor(AbstractExecutor):
    """
    Applies predicates to filter the frames which satisfy the condition
    Arguments:
        node (AbstractPlan): The SequentialScanPlan

    """

    def __init__(self, node: 'AbstractPlan'):
        super().__init__(node)
        self.predicate = node.predicate

    def validate(self):
        pass

    def next(self) -> Iterator[FrameBatch]:

        child_executor = self.children[0]
        for batch in child_executor.next():
            if self.predicate is not None:
                outcomes = self.predicate.evaluate(batch)
                required_frame_ids = []
                for i, outcome in enumerate(outcomes):
                    if outcome:
                        required_frame_ids.append(i)

                yield batch[required_frame_ids]

            else:
                yield batch
