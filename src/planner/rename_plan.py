from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanOprType
from src.parser.table_ref import TableRef, TableInfo


# Modified
class RenamePlan(AbstractPlan):
    """
    This plan is used for storing information required for rename table
    operations.
    Arguments:
        old_table {TableRef} -- table ref for table to be renamed in storage
        table_id {int} -- catalog table id for the table
        new_name {TableInfo} -- new name of old_table
    """

    def __init__(self, old_table: TableRef, 
                 table_id: int,
                 new_name: TableInfo):
        super().__init__(PlanOprType.RENAME)
        self._old_table = old_table
        self._table_id = table_id
        self._new_name = new_name

    @property
    def old_table(self):
        return self._old_table

    @property
    def table_id(self):
        return self._table_id

    @property
    def new_name(self):
        return self._new_name