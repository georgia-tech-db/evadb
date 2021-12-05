from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanOprType
from typing import List
from src.parser.table_ref import TableRef


class TruncatePlan(AbstractPlan):
    """
    This plan is used for storing information required for truncate table
    operations.
    Arguments:
        table_ref {TableRef} -- table ref for table to be truncated in storage
        table_id {int} -- catalog table id for the table
    """

    def __init__(self, table_ref: TableRef,
                 table_id: int):
        super().__init__(PlanOprType.TRUNCATE)
        self._table_ref = table_ref
        self._table_id = table_id

    @property
    def table_ref(self):
        return self._table_ref

    @property
    def table_id(self):
        return self._table_id

    #@property
    #def if_not_exists(self):
    #    return self._if_not_exists
