from typing import Iterator

from src.loaders.video_loader import VideoLoader
from src.models.storage.batch import FrameBatch
from src.query_executor.abstract_storage_executor import \
    AbstractStorageExecutor
from src.query_planner.storage_plan import StoragePlan


class DiskStorageExecutor(AbstractStorageExecutor):
    """
    This is a simple disk based executor. It assumes that frames are
    directly being read from the disk(video file).

    Note: For a full fledged deployment this might be replaced with a
    Transaction manager which keeps track of the frames.
    """

    def __init__(self, node: StoragePlan):
        super().__init__(node)
        self.storage = VideoLoader(node.video,
                                         batch_size=node.batch_size,
                                         skip_frames=node.skip_frames,
                                         limit=node.limit,
                                         offset=node.offset)

    def validate(self):
        pass

    def next(self) -> Iterator[FrameBatch]:
        for batch in self.storage.load():
            yield batch
