from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanOprType
from typing import List
from src.parser.table_ref import TableRef


class DropPlan(AbstractPlan):
    """
    This plan is used for storing information required for drop table
    operations.
    Arguments:
        table_ref {TableRef} -- table ref for table to be truncated in storage
        table_id {int} -- catalog table id for the table
    """

    def __init__(self, table_refs: List[TableRef],
                 if_exists: bool,
                 table_ids: List[int]):
        super().__init__(PlanOprType.DROP)
        self._table_refs = table_refs
        self._table_ids = table_ids
        self._if_exists = if_exists

    @property
    def table_refs(self):
        return self._table_refs

    @property
    def table_ids(self):
        return self._table_ids

    @property
    def if_exists(self):
        return self._if_exists
