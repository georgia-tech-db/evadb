from typing import List
from src.parser.statement import AbstractStatement

from src.parser.types import StatementType
from src.parser.table_ref import TableRef


class DropTableStatement(AbstractStatement):
    """Drop Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the truncate table statement
    """

    def __init__(self,
                 table_refs: List[TableRef],
                 if_exists: bool):
        super().__init__(StatementType.DROP)
        self._table_refs = table_refs
        self._if_exists = if_exists

    def __str__(self) -> str:
        if self._if_exists:
            print_str = "DROP TABLE IF EXISTS {}".format(self._table_refs)
        else:
            print_str = "DROP TABLE {}".format(self._table_refs)
        return print_str

    @property
    def table_refs(self):
        return self._table_refs

    @property
    def if_exists(self):
        return self._if_exists

    def __eq__(self, other):
        if not isinstance(other, DropTableStatement):
            return False
        print(self.table_refs, '==', other.table_refs)
        return (self.table_refs == other.table_refs
                and self.if_exists == other.if_exists)
        # and self.if_exists == other.if_exists)
