from src.parser.statement import AbstractStatement

from src.parser.types import StatementType
from src.parser.table_ref import TableRef

class TruncateTableStatement(AbstractStatement):
    """Truncate Table Statement constructed after parsing the input query

    Attributes:
        TableRef: table reference in the truncate table statement
    """

    def __init__(self,
                 table_ref: TableRef):
        super().__init__(StatementType.TRUNCATE)
        self._table_ref = table_ref

    def __str__(self) -> str:
        print_str = "TRUNCATE TABLE {}".format(self._table_ref)
        return print_str

    @property
    def table_ref(self):
        return self._table_ref

    def __eq__(self, other):
        if not isinstance(other, TruncateTableStatement):
            return False
        return (self.table_ref == other.table_ref)
                #and self.if_exists == other.if_exists)
