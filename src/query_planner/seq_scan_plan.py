
from query_planner.abstract_scan_plan import AbstractScan
from src.query_planner.abstract_plan import PlanNodeType
class SeqScanPlan(AbstractScan):
    def __init__(self, predicate : Expression, video : Storage, column_ids : List[int]):
        super(SeqScanPlan, self, predicate, video, column_ids).__init__()

    def get_node_type(self):
        return PlanNodeType.SEQSCAN

    #ToDo Add other functionality based on optimiser

    

    