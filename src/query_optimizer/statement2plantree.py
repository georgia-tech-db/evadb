from query_planner.logical_projection_plan import LogicalProjectionPlan
from query_planner.seq_scan_plan import SeqScanPlan
from src.query_parser.table_ref import TableRef, TableInfo
from src.loaders.video_loader import SimpleVideoLoader
from src.models.catalog.video_info import VideoMetaInfo
from src.models.catalog.properties import VideoFormat

# class that will handle converting a statement to a plan tree
class Statement2Plantree:
    def __init__(self):
        pass

    # Function that converts the statement list to a plan tree
    # Inputs: Statement_list : list of Select Statement objects
    # Outputs: root node of plan tree. Will be of type LogicalProjectionPlan.
    @staticmethod
    def convert(statement_list):
        if len(statement_list) > 1 or len(statement_list) == 0:
            print('statement list must be length 1 and it was len: {}'.format(len(statement_list)))
        else:
            statement = statement_list[0]
            # Need to Create the table and projection
            from_stuff = statement.from_table
            meta1 = VideoMetaInfo(file=from_stuff.table_info.table_name, c_format=VideoFormat.MOV, fps=30)
            video1 = SimpleVideoLoader(video_metadata=meta1)
            t1 = TableRef(video=video1, table_info=TableInfo(table_name=from_stuff.table_info.table_name))
            # Creating projection (root)
            projection_output = [target.col_name for target in statement.target_list]
            root = LogicalProjectionPlan(videos=[video1], column_ids=projection_output, foreign_column_ids=[])
            where_stuff = statement.where_clause
            print(where_stuff)
            # Need to create the sigma plan
            if where_stuff is not None:
                # Creating a select Node
                select_node = SeqScanPlan(predicate=where_stuff, column_ids=projection_output, videos=[video1], foreign_column_ids=[])
                root.set_children(select_node)
                select_node.parent=root
                select_node.set_children([t1])
                t1.parent=select_node
            else:
                root.set_children([t1])
                t1.parent = root
            return root

