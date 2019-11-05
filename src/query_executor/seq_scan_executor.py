from src.models import FrameBatch, Predicate
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

    def execute(self, batch: FrameBatch):
        predictions = batch.get_outcomes_for(self.predicate.name)
        required_frame_ids = []
        for i, prediction in enumerate(predictions):
            if self.predicate(prediction):
                required_frame_ids.append(i)

        return batch[required_frame_ids]
