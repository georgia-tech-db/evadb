"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from src.loaders.abstract_loader import AbstractVideoLoader
from typing import List


class AbstractInnerJoin(AbstractPlan):
    """Abstract class for all the inner join based planners

    Arguments:
        predicate : Expression
        videos : list of videos on which the join will be executed
        join_id : columns that will be joined on in the form of "tablename.attribute"

    """

    def __init__(self, videos: List[AbstractVideoLoader], join_ids: List[str]):
        super(AbstractInnerJoin, self).__init__()
        self._join_ids = join_ids
        self._videos = videos


    @property
    def videos(self) -> List[AbstractVideoLoader]:
        return self._videos

    @property
    def join_ids(self) -> List[int]:
        return self._join_ids


    def __str__(self, level=0):
        pt1 = ' join '.join([str(video.video_metadata.file) for video in self.videos])
        pt2 = ' = '.join([str(id) for id in self._join_ids])
        res = '{}__{}'.format(pt1, pt2)
        ret = "\t" * level + res + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret
