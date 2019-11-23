from typing import List

from src.models.storage.batch import FrameBatch


class DummyExecutor:
    def __init__(self, batch_list: List[FrameBatch]):
        self.batch_list = batch_list

    def next(self):
        for batch in self.batch_list:
            yield batch
