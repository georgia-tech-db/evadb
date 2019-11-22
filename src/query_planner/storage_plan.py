from src.models.catalog.video_info import VideoMetaInfo
from src.query_planner.abstract_plan import AbstractPlan
from src.query_planner.types import PlanNodeType


class StoragePlan(AbstractPlan):
    """
    This is the plan used for retrieving the frames from the storage and
    and returning to the higher levels.
    """

    def __init__(self, video: VideoMetaInfo, batch_size: int = 1,
                 skip_frames: int = 0, offset: int = None, limit: int = None):
        super().__init__(PlanNodeType.STORAGE_PLAN)
        self._video = video
        self._batch_size = batch_size
        self._skip_frames = skip_frames
        self._offset = offset
        self._limit = limit

    @property
    def video(self):
        return self._video

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def skip_frames(self):
        return self._skip_frames

    @property
    def offset(self):
        return self._offset

    @property
    def limit(self):
        return self._limit
