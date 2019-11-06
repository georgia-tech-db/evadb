from src.models import VideoMetaInfo, Predicate
from src.planner.abstract_plan import AbstractPlan
from src.planner.types import NodeType


class SeqScanPlan(AbstractPlan):
    def __init__(self,  predicate: Predicate=None):
        super().__init__(NodeType.SEQUENTIAL_SCAN_TYPE)
        #self._video_meta_info = video
        self._predicate = predicate

    @property
    def predicate(self):
        return self._predicate


