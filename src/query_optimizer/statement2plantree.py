from src.query_parser.select_statement import SelectStatement
from query_planner.logical_select_plan import LogicalSelectPlan
from query_planner.logical_inner_join_plan import LogicalInnerJoinPlan
from query_planner.logical_projection_plan import LogicalProjectionPlan
from query_planner.video_table_plan import VideoTablePlan
from loaders.video_loader import SimpleVideoLoader
from models.catalog.video_info import VideoMetaInfo
from models.catalog.properties import VideoFormat


# class that will handle converting a statement to a plan tree
class Statement2Plantree:
    def __init__(self):
        pass

    # Function that converts the statement list to a plan tree
    # Inputs: Statement_list : list of Select Statement objects
    # Outputs: root node of plan tree. Will be of type LogicalProjectionPlan.
    @staticmethod
    def convert(statement_list):
        if len(statement_list) > 1:
            print('nested queries are not handled yet')
        else:
            statement = statement_list[0]
            # Need to Create the table and projection
            from_stuff = statement.from_table
            meta1 = VideoMetaInfo(file=from_stuff.table_info.table_name, c_format=VideoFormat.MOV, fps=30)
            video1 = SimpleVideoLoader(video_metadata=meta1)
            t1 = VideoTablePlan(video=video1, tablename=from_stuff.table_info.table_name)
            # Creating projection (root)
            projection_output = [target.col_name for target in statement.target_list]
            root = LogicalProjectionPlan(videos=[video1], column_ids=projection_output, foreign_column_ids=[])
            where_stuff = statement.where_clause
            # Need to create the sigma plan
            if where_stuff is not None:
                pass
            else:
                root.set_children([t1])
                t1.parent = root
            return root

