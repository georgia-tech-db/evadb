"""Abstract class for all the scan planners
https://www.postgresql.org/docs/9.1/using-explain.html
https://www.postgresql.org/docs/9.5/runtime-config-query.html
"""
from src.query_planner.abstract_plan import AbstractPlan
from src.loaders.abstract_loader import AbstractVideoLoader


class AbstractTable(AbstractPlan):
    """Abstract class for all the table based planners
       Basically used to represent a table at the bottom of the logical plan tree
       Note that this implementation assumes that each video is a table like in Blazeit
    Arguments:
        video : video encapsulated by the table
    """

    def __init__(self, video: AbstractVideoLoader, tablename: str):
        super(AbstractTable, self).__init__()
        self._video = video
        self._tablename = tablename

    @property
    def video(self) -> AbstractVideoLoader:
        return self._video

    @property
    def tablename(self) -> str:
        return self._tablename

    def __str__(self, level=0):
        res = '{}'.format(str(self.video.video_metadata.file))
        ret = "\t" * level + res + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret
