from src.storage.abstract_loader import AbstractVideoLoader
from src.query_planner.abstract_table_plan import AbstractTable
from src.query_planner.abstract_plan import PlanNodeType


class VideoTablePlan(AbstractTable):
    """Class for all the table based planners
       Basically used to represent a table at the bottom of the logical plan tree
       Note that this implementation assumes that each video is a table like in Blazeit
    Arguments:
        video : video encapsulated by the table
    """

    def __init__(self, video: AbstractVideoLoader, tablename: str):
        super().__init__(video, tablename)

    def get_node_type(self):
        return PlanNodeType.TABLE

    # ToDo Add other functionality based on optimiser